from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import json

# Configuração inicial
URL_LOGIN = "https://loja.hayamax.com.br/entrar-cliente?return_to=https%3A%2F%2Fhayamax.com.br%2F"
LOGIN = "1 1 5 5 8 3 9 1 0 0 0 1 8 0"
SENHA = "Adw@0412"

# Categorias e URLs
CATEGORIAS = {
    "Teclas": "https://loja.hayamax.com.br/categoria/instrumentos-musicais-teclas",
    "Violões": "https://loja.hayamax.com.br/categoria/instrumentos-musicais-cordas-violoes",
    "Guitarras": "https://loja.hayamax.com.br/categoria/instrumentos-musicais-cordas-guitarras"
}

# Reajustes por categoria
REAJUSTES = {
    "Teclas": 1.20,
    "Violões": 1.20,
    "Guitarras": 1.20,
}

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

def fazer_login():
    driver.get(URL_LOGIN)
    wait.until(EC.presence_of_element_located((By.ID, "customer[stcd1]"))).send_keys(LOGIN)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.ID, "btn-login"))).click()
    print("✅ Login realizado com sucesso!")

def ordenar_por_maior_preco(url):
    driver.get(url)
    time.sleep(3)

    # Tenta fechar o banner LGPD
    try:
        lgpd = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "footer-lgpd-btn"))
        )
        lgpd.click()
        print("✅ Banner LGPD clicado para fechar.")
        # Aguarda o sumiço do banner
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element((By.ID, "footer-lgpd"))
        )
        print("✅ Banner LGPD sumiu da tela.")
    except:
        print("ℹ️ Banner LGPD não encontrado ou já fechado.")

    # Continua com a ordenação
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "filter[config][sort_by]"))
        )
        select_element.click()
        print("✅ Dropdown de ordenação clicado.")
        maior_preco_option = wait.until(
            EC.presence_of_element_located((By.XPATH, "//option[@value='precoZA']"))
        )
        maior_preco_option.click()
        print("🔄 Produtos ordenados por maior preço.")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Erro ao ordenar por preço: {e}")

def carregar_todos_produtos(url):
    time.sleep(5)
    while True:
        try:
            produtos_atuais = len(driver.find_elements(By.CLASS_NAME, "search-product"))
            try:
                btn_ver_mais = wait.until(EC.element_to_be_clickable((By.ID, "btn-more")))
                btn_ver_mais.click()
                print("🔄 Carregando mais produtos...")
                time.sleep(3)
            except:
                break
            novos_produtos = len(driver.find_elements(By.CLASS_NAME, "search-product"))
            if novos_produtos == produtos_atuais:
                break
        except Exception as e:
            print(f"❌ Erro ao tentar carregar mais produtos: {e}")
            break

def coletar_produtos(nome_categoria):
    produtos = driver.find_elements(By.CLASS_NAME, "search-product")
    print(f"🔍 Total de produtos encontrados em {nome_categoria}: {len(produtos)}")

    dados = {nome_categoria: []}
    reajuste = REAJUSTES.get(nome_categoria, 1.17)

    for idx, p in enumerate(produtos):
        try:
            nome = p.find_element(By.CLASS_NAME, "search-product-title").text.strip()
            codigo = p.find_element(By.CLASS_NAME, "search-product-matnr").text.strip()
            codigo = re.sub(r"[^\d]", "", codigo)

            preco_elementos = p.find_elements(By.CLASS_NAME, "search-product-price-sales") or p.find_elements(By.CLASS_NAME, "search-product-price")
            preco = preco_elementos[0].text.strip()
            preco = re.sub(r"[^\d,]", "", preco)
            preco = float(preco.replace(",", ".")) * reajuste
            preco_formatado = f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            try:
                imagem_element = p.find_element(By.CSS_SELECTOR, "img.search-product-image")
                imagem = imagem_element.get_attribute("src")
                # Se for placeholder GIF (imagem transparente), tenta pegar o data-src
                if imagem.startswith("data:image/gif;base64"):
                    data_src = imagem_element.get_attribute("data-src")
                    if data_src and data_src.startswith("http"):
                        imagem = data_src
            except:
                imagem = "Imagem não disponível"



            # Abrir página do produto
            link_produto = p.find_element(By.TAG_NAME, "a").get_attribute("href")
            driver.execute_script("window.open(arguments[0]);", link_produto)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)

            # Descrição
            try:
                descricao_element = driver.find_element(By.XPATH, '//*[@id="hyx-tab1"]/div[2]')
                descricao = descricao_element.text.strip()
            except:
                descricao = ""

            # Imagens adicionais
            imagens_adicionais = []
            thumbs = driver.find_elements(By.CSS_SELECTOR, ".thumbs img")
            for thumb in thumbs:
                img_src = thumb.get_attribute("src")
                if img_src and img_src.startswith("http"):
                    imagens_adicionais.append(img_src)
                if len(imagens_adicionais) >= 3:
                    break

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            dados[nome_categoria].append((
                nome,
                codigo,
                preco_formatado,
                imagem,
                descricao,
                imagens_adicionais
            ))

        except Exception as e:
            print(f"❌ Erro ao coletar produto {idx + 1}: {e}")
    
    return dados

def salvar_json(dados_por_categoria, arquivo="produtos_hayamax.json"):
    produtos_json = {}
    for categoria, dados in dados_por_categoria.items():
        produtos_json[categoria] = []
        for produto in dados:
            produto_dict = {
                "Nome": produto[0],
                "Código": produto[1],
                "Preço": produto[2],
                "Imagem (URL)": produto[3],
                "Descrição": produto[4],
                "Imagens adicionais": produto[5]
            }
            produtos_json[categoria].append(produto_dict)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos_json, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Arquivo JSON '{arquivo}' gerado com sucesso!")

# Executa
fazer_login()

dados_por_categoria = {}

for nome_categoria, url_categoria in CATEGORIAS.items():
    print(f"\n🔄 Categoria: {nome_categoria}")
    ordenar_por_maior_preco(url_categoria)
    carregar_todos_produtos(url_categoria)
    produtos = coletar_produtos(nome_categoria)
    if produtos:
        dados_por_categoria.update(produtos)

if dados_por_categoria:
    salvar_json(dados_por_categoria)

driver.quit()

