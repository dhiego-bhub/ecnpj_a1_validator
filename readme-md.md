# Validador de Certificado Digital

Aplicação web simples para validar certificados digitais A1 (PFX/P12) utilizando Python e Streamlit.

## Funcionalidades

- Upload de arquivos de certificado digital no formato PFX ou P12
- Validação da senha do certificado
- Exibição das informações do certificado:
  - Nome do titular
  - Organização
  - E-mail (se disponível)
  - Período de validade
  - Status atual de validade
  - Dias restantes até a expiração

## Como usar

1. Faça upload do seu arquivo de certificado (.pfx ou .p12)
2. Digite a senha do certificado no campo apropriado
3. Visualize as informações do certificado

## Tecnologias utilizadas

- Python
- Streamlit
- Cryptography (biblioteca para manipulação de certificados)

## Como executar localmente

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```
   streamlit run app.py
   ```

## Privacidade e Segurança

Esta aplicação processa os certificados digitais localmente no navegador. Nenhuma informação é armazenada em servidores externos ou compartilhada com terceiros.
