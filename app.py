import streamlit as st
import google.generativeai as genai
import io
import time
from pydub import AudioSegment

# API Key സെറ്റ് ചെയ്യുക (Streamlit Secrets വഴി നൽകുന്നത് സുരക്ഷിതമാണ്)
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Malayalam Text-to-Speech (Leda Voice)")
user_text = st.text_area("നിങ്ങളുടെ വലിയ മലയാളം ടെക്സ്റ്റ് ഇവിടെ നൽകുക:", height=300)

def chunk_text(text, max_chars=1000):
    # വലിയ ടെക്സ്റ്റിനെ ചെറിയ ഭാഗങ്ങളാക്കി മാറ്റാനുള്ള ഫംഗ്ഷൻ
    return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

if st.button("Generate Audio"):
    if user_text:
        st.info("ഓഡിയോ തയ്യാറാക്കുന്നു... ദയവായി കാത്തിരിക്കുക.")
        chunks = chunk_text(user_text)
        combined_audio = AudioSegment.empty()

        try:
            for chunk in chunks:
                # ഇവിടെ നിങ്ങളുടെ Google AI Studio TTS ലോജിക്/API Call വരും.
                # Leda വോയിസ് പാരാമീറ്റർ ആയി നൽകുക.
                
                # API യിൽ നിന്ന് ലഭിക്കുന്ന ഓഡിയോ pydub ഉപയോഗിച്ച് ചേർക്കുന്ന വിധം:
                # chunk_audio = AudioSegment.from_file(io.BytesIO(api_response_audio), format="mp3")
                # combined_audio += chunk_audio
                
                # API Rate limit ഒഴിവാക്കാൻ ചെറിയ ഇടവേള നൽകാം
                time.sleep(2) 
            
            # ഫൈനൽ ഓഡിയോ പ്ലേ ചെയ്യാൻ
            # audio_bytes = io.BytesIO()
            # combined_audio.export(audio_bytes, format="mp3")
            # st.audio(audio_bytes.getvalue(), format="audio/mp3")
            st.success("ഓഡിയോ തയ്യാറാണ്!")
        except Exception as e:
            st.error(f"എന്തോ കുഴപ്പമുണ്ടായി: {e}")
            # ഫൈനൽ ഓഡിയോ പ്ലേ ചെയ്യാനുള്ള പഴയ കോഡ്
audio_bytes = io.BytesIO()
combined_audio.export(audio_bytes, format="mp3")
audio_data = audio_bytes.getvalue()

st.audio(audio_data, format="audio/mp3")

# ഇതിന് താഴെയായി ഡൗൺലോഡ് ബട്ടൺ ചേർക്കാൻ താഴെയുള്ള കോഡ് നൽകുക:
st.download_button(
    label="ഓഡിയോ ഡൗൺലോഡ് ചെയ്യുക 📥",
    data=audio_data,
    file_name="malayalam_speech.mp3",
    mime="audio/mp3"
)
