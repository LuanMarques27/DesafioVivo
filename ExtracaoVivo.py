from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import time
import re

url_extract = "https://store.vivo.com.br/"
cep = "87430-000"

#configurando o banco
engine = create_engine('sqlite:///celulares.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

#Mapeamento do banco conforme solicitado
class Celulares(Base):
     __tablename__ = 'Celulares'
     
     id = Column("id", Integer, primary_key=True)
     Modelo = Column("Modelo", String(50))
     Capacidade = Column("Capacidade", String(10))
     TamanhoTela = Column("TamanhoTela", String(10))
     PrecoTotal = Column("PrecoTotal", String(10))
     ValorParcela = Column("ValorParcela", String(20))
     Cor = Column("Cor", String(20))
     UltimasPecas = Column("UltimasPecas", Boolean)

     def __init__(self, Modelo, Capacidade, TamanhoTela, PrecoTotal, ValorParcela, Cor, UltimasPecas):
         self.Modelo = Modelo
         self.Capacidade = Capacidade
         self.TamanhoTela = TamanhoTela
         self.PrecoTotal = PrecoTotal
         self.ValorParcela = ValorParcela
         self.Cor = Cor
         self.UltimasPecas = UltimasPecas


#iniciando banco
Base.metadata.create_all(bind=engine)

#instanciando o pdf para saida
cnv = canvas.Canvas("celularCompra.pdf", pagesize=A4)

#abrindo o navegador fazendo a instalação do driver para controle do selenium
servico = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servico)
navegador.get(url_extract)
#colocando o tempo de espera para cada procura dos elementos em 10 secs
navegador.implicitly_wait(5)
navegador.maximize_window()

#aceitando os cooks pois aviso atrapalha a navegação
navegador.find_element(By.XPATH,'//button[@class="vsp-button primary contained size-1"]').click()

#fazendo a pesquisa dos celulares
navegador.find_element(By.XPATH,'//button[@class="searchbox__button"]').click()
navegador.find_element(By.XPATH,'//input[@id="inputSearch"]').send_keys("celulares apple")
navegador.find_element(By.XPATH,'//i[@role="button"]').click()


#arrumando os filtros
navegador.find_element(By.XPATH,'//input[@name="Celular-checkbox"]').click()
time.sleep(2)
navegador.find_element(By.XPATH,'//input[@name="Apple-checkbox"]').click()
time.sleep(2)
navegador.find_element(By.XPATH,'//div[@class="vsp-select__input__option-labels"]').click()
time.sleep(1)
navegador.find_element(By.XPATH,'//li[@aria-label="Preço (maior primeiro)"]').click()
time.sleep(2)

#definindo as mascaras de RE para captura
mascaraModelo = r'Apple\D*\d+\D*'
mascaraTamanho = r'\d+(GB|TB)'
mascaraTela = r'\d,\d\"'
mascaraCor = r'\d+(TB|GB)\D+'
mascaraCorRemove = r'[^\d+(GB|TB) ]\D+'
mascaraValorTotal = r'R\$ \d+\.\d+,\d+'
mascaraValorParcela = r'R\$ \d(\.|)\d+,\d+ (sem|com) juros'

#fazendo a extraçao
captura = 0
while (captura <= 50):
    if captura == 0:
        celularesBusca = navegador.find_elements(By.XPATH,'//a[@class="product-card product-card--grid"]')
        for celular in celularesBusca:
            if 'Poxa, esse produto acabou' in celular.text:
                continue
            else:
                modelo = re.search(mascaraModelo, celular.text).group()
                tamanho = re.search(mascaraTamanho, celular.text).group()
                tela = re.search(mascaraTela, celular.text).group()
                cor = re.search(mascaraCor, celular.text).group()
                cor = re.search(mascaraCorRemove, cor).group()
                valorTotal = re.search(mascaraValorTotal, celular.text).group()
                valorParcelaSite = re.search(mascaraValorParcela, celular.text).group()
                if 'Peças' in celular.text:
                    ultimaPeças = True
                else:
                    ultimaPeças = False
                celular.click()
                time.sleep(2)
                navegador.find_element(By.XPATH,'//input[@id="postalCode"]').send_keys(cep)
                time.sleep(1)
                navegador.find_element(By.XPATH,'//button[@id="applyPostalCode"]').click()
                time.sleep(2)
                entrega = navegador.find_element(By.XPATH,'//span[@class="product-delivery-time__content-wrapper__delivery-time__result__days"]').text
                descricao = navegador.find_element(By.XPATH,'//div[@class="custom-product-details-tab"]').text
                navegador.back()
                time.sleep(3)
                cnv.drawString(50, 800, modelo)
                cnv.drawString(50, 785, tamanho)
                cnv.drawString(90, 785, tela)
                cnv.drawString(50, 770, valorTotal)
                cnv.drawString(50, 755, entrega)
                tam = len(descricao)
                line = 735
                for step in range(0, tam, 80):
                    tot = step+80
                    line = line - 15
                    if tot < tam:
                        cnv.drawString(50, line, descricao[step:tot])
                    else:
                        cnv.drawString(50, line, descricao[step:tam])
                cnv.save()
                captura = captura + 1
                break
    
    celularesBusca = navegador.find_elements(By.XPATH,'//a[@class="product-card product-card--grid"]')
    for celular in celularesBusca:
        if 'Poxa, esse produto acabou' in celular.text:
            continue
        else:
            modelo = re.search(mascaraModelo, celular.text).group()
            tamanho = re.search(mascaraTamanho, celular.text).group()
            tela = re.search(mascaraTela, celular.text).group()
            cor = re.search(mascaraCor, celular.text).group()
            cor = re.search(mascaraCorRemove, cor).group()
            valorTotal = re.search(mascaraValorTotal, celular.text).group()
            valorParcelaSite = re.search(mascaraValorParcela, celular.text).group()
            if 'Peças' in celular.text:
                ultimaPeças = True
            else:
                ultimaPeças = False
            celularnovo = Celulares(Modelo=modelo, Capacidade=tamanho, TamanhoTela=tela, PrecoTotal=valorTotal, ValorParcela=valorParcelaSite, Cor=cor, UltimasPecas=ultimaPeças)
            session.add(celularnovo)
            session.commit()
            captura = captura + 1
    next = navegador.find_elements(By.XPATH,'//a[@class="end"]')
    if next:
        navegador.find_element(By.XPATH,'//a[@class="end"]').click() 
    else:
        break
    time.sleep(3)  
navegador.close

