import streamlit as st
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509 import NameOID
import io
import datetime
import pytz

st.set_page_config(
    page_title="Validador de Certificado Digital",
    page_icon="🔐",
    layout="centered"
)

def main():
    st.title("Validador de Certificado Digital")
    
    st.markdown("""
    Esta aplicação permite validar certificados digitais A1 (PFX/P12).
    
    Faça upload do seu arquivo de certificado e informe a senha para visualizar suas informações.
    """)
    
    # Upload do arquivo de certificado
    uploaded_file = st.file_uploader("Faça upload do seu certificado (.pfx ou .p12)", type=["pfx", "p12"])
    
    # Campo para a senha
    pfx_password = st.text_input("Digite a senha do certificado", type="password")
    
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
            st.error(f"Erro ao processar o certificado: {str(e)}")
            st.error("Verifique se a senha está correta ou se o arquivo é válido.")

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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Nome do Titular**")
        st.info(info["common_name"])
        
        st.write("**Organização**")
        st.info(info["organization"])
        
        st.write("**E-mail**")
        st.info(info["email"])
    
    with col2:
        st.write("**Válido a partir de**")
        st.info(info["not_before"].strftime("%d/%m/%Y %H:%M:%S"))
        
        st.write("**Válido até**")
        st.info(info["not_after"].strftime("%d/%m/%Y %H:%M:%S"))
        
        st.write("**Status**")
        if info["is_valid"]:
            st.success(f"✅ Válido (Expira em {info['days_remaining']} dias)")
        else:
            if info["days_remaining"] < 0:
                st.error(f"❌ Expirado (Há {abs(info['days_remaining'])} dias)")
            else:
                st.warning(f"⚠️ Ainda não válido")

if __name__ == "__main__":
    main()
