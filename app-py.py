import streamlit as st
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import NameOID
import io
import datetime
import pytz

st.set_page_config(
    page_title="Validador de Certificado Digital",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Personalização global do tema
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    .stApp {
        background-color: #121212;
        color: white;
    }
    h1, h2, h3 {
        color: white;
    }
    .stButton button {
        background-color: #1E3A5F;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #2E5A8F;
    }
    .stTextInput input, .stFileUploader {
        border-radius: 5px;
    }
    div[data-testid="stFileUploader"] {
        background-color: #1E3A5F;
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stFileUploader"] button {
        background-color: #4169E1;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <h1 style="text-align: center; margin-bottom: 2rem;">
        <span style="color: #4169E1;">🔐 Validador de Certificado Digital</span>
    </h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #1E3A5F; padding: 15px; border-radius: 5px; margin-bottom: 30px;">
        <p>Esta aplicação permite validar certificados digitais A1 (PFX/P12).</p>
        <p>Faça upload do seu arquivo de certificado e informe a senha para visualizar suas informações.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializa as variáveis de estado para controle
    if 'last_uploaded_file' not in st.session_state:
        st.session_state.last_uploaded_file = None
    
    # Upload do arquivo de certificado
    uploaded_file = st.file_uploader("Faça upload do seu certificado (.pfx ou .p12)", type=["pfx", "p12"])
    
    # Verificar se o arquivo foi alterado
    if uploaded_file is not None and (st.session_state.last_uploaded_file is None or 
                                     uploaded_file.name != st.session_state.last_uploaded_file):
        # Atualiza o arquivo na sessão
        st.session_state.last_uploaded_file = uploaded_file.name
        # Limpa o campo de senha usando JavaScript
        st.markdown("""
        <script>
            setTimeout(function() {
                document.querySelector('input[type="password"]').value = '';
            }, 100);
        </script>
        """, unsafe_allow_html=True)
        # Força a reinicialização da senha no estado da sessão
        if 'password' in st.session_state:
            del st.session_state.password
    
    # Campo para a senha com estado de sessão
    if 'password' not in st.session_state:
        st.session_state.password = ""
    
    pfx_password = st.text_input("Digite a senha do certificado", type="password", key="password")
    
    if uploaded_file is not None and pfx_password:
        try:
            # Converter a senha para bytes
            password = pfx_password.encode()
            
            # Ler os dados do arquivo
            pfx_data = uploaded_file.getvalue()
            
            # Processar o certificado
            certificate_info = process_certificate(pfx_data, password)
            
            # Exibir as informações do certificado
            display_certificate_info(certificate_info)
            
        except Exception as e:
            st.markdown("""
            <div style="background-color: #CF0000; color: white; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h3 style="margin-top: 0;">❌ Erro ao processar o certificado</h3>
                <p>Verifique se a senha está correta ou se o arquivo é válido.</p>
                <details>
                    <summary>Detalhes técnicos</summary>
                    <code style="color: #EEEEEE; display: block; margin-top: 10px; word-break: break-all;">
            """, unsafe_allow_html=True)
            st.code(str(e), language="")
            st.markdown("""
                    </code>
                </details>
            </div>
            """, unsafe_allow_html=True)

def process_certificate(pfx_data, password):
    # Carregar o certificado PFX
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(pfx_data, password)
    
    # Extrair a validade do certificado
    not_before = certificate.not_valid_before_utc
    not_after = certificate.not_valid_after_utc
    
    # Extrair o nome do titular do certificado
    subject = certificate.subject
    common_name = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    
    # Extrair outras informações relevantes, se disponíveis
    try:
        organization = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value
    except IndexError:
        organization = "N/A"
    
    try:
        email = subject.get_attributes_for_oid(NameOID.EMAIL_ADDRESS)[0].value
    except IndexError:
        email = "N/A"
    
    # Formatação de datas para exibição
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    not_before_br = not_before.astimezone(brazil_tz)
    not_after_br = not_after.astimezone(brazil_tz)
    
    # Verificar se o certificado está válido
    now = datetime.datetime.now(datetime.timezone.utc)
    is_valid = not_before <= now <= not_after
    
    # Calcular dias restantes
    days_remaining = (not_after - now).days
    
    return {
        "common_name": common_name,
        "organization": organization,
        "email": email,
        "not_before": not_before_br,
        "not_after": not_after_br,
        "is_valid": is_valid,
        "days_remaining": days_remaining
    }

def display_certificate_info(info):
    st.success("Certificado carregado com sucesso!")
    
    st.subheader("Informações do Certificado")
    
    # Estilo CSS personalizado para melhorar o alinhamento
    st.markdown("""
    <style>
    .info-container {
        width: 100%;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 30px;
    }
    .info-item {
        display: flex;
        flex-direction: column;
    }
    .info-label {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 16px;
    }
    .info-value {
        background-color: #1E3A5F;
        color: white;
        padding: 12px 15px;
        border-radius: 5px;
        min-height: 50px;
        display: flex;
        align-items: center;
        word-break: break-word;
    }
    .status-container {
        margin-bottom: 30px;
        width: 100%;
    }
    .status-label {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 18px;
    }
    .status-valid {
        background-color: #0E6B0E;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    .status-expired {
        background-color: #CF0000;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    .status-warning {
        background-color: #F39C12;
        color: white;
        padding: 15px;
        border-radius: 5px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Status destacado no topo
    st.markdown('<div class="status-label">Status</div>', unsafe_allow_html=True)
    if info["is_valid"]:
        st.markdown(f'<div class="status-valid">✅ VÁLIDO (Expira em {info["days_remaining"]} dias)</div>', unsafe_allow_html=True)
    else:
        if info["days_remaining"] < 0:
            st.markdown(f'<div class="status-expired">❌ EXPIRADO (Há {abs(info["days_remaining"])} dias)</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-warning">⚠️ AINDA NÃO VÁLIDO</div>', unsafe_allow_html=True)
    
    # Layout em grid para os demais campos
    st.markdown('<div class="info-container">', unsafe_allow_html=True)
    
    # Coluna 1
    st.markdown("""
        <div class="info-item">
            <div class="info-label">Nome do Titular</div>
            <div class="info-value">PLACEHOLDER_COMMON_NAME</div>
        </div>
    """.replace("PLACEHOLDER_COMMON_NAME", info["common_name"]), unsafe_allow_html=True)
    
    # Coluna 2
    st.markdown("""
        <div class="info-item">
            <div class="info-label">Válido a partir de</div>
            <div class="info-value">PLACEHOLDER_NOT_BEFORE</div>
        </div>
    """.replace("PLACEHOLDER_NOT_BEFORE", info["not_before"].strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)
    
    # Coluna 3
    st.markdown("""
        <div class="info-item">
            <div class="info-label">Organização</div>
            <div class="info-value">PLACEHOLDER_ORGANIZATION</div>
        </div>
    """.replace("PLACEHOLDER_ORGANIZATION", info["organization"]), unsafe_allow_html=True)
    
    # Coluna 4
    st.markdown("""
        <div class="info-item">
            <div class="info-label">Válido até</div>
            <div class="info-value">PLACEHOLDER_NOT_AFTER</div>
        </div>
    """.replace("PLACEHOLDER_NOT_AFTER", info["not_after"].strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
