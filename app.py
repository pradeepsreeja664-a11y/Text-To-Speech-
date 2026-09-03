import streamlit as st
from google import genai
from google.genai import types
import os

# വെബ്സൈറ്റ് പേജും ഡിസൈനും സെറ്റ് ചെയ്യുന്നു
st.set_page_config(page_title="മലയാളം Text to Speech", page_icon="🎙️", layout="centered")

st.title("🎙️ Gemini മലയാളം Text to Speech")
st.write("Gemini API ഉപയോഗിച്ച് എത്ര വലിയ മലയാളം ടെക്സ്റ്റും വോയ്സ് ആക്കി മാറ്റാം.")

# GitHub-ൽ ഹോസ്റ്റ് ചെയ്യുമ്പോൾ സുരക്ഷയ്ക്കായി സെറ്റിങ്സ് പേജിൽ നിന്നും കീ എടുക്കുന്നു
# അല്ലെങ്കിൽ യൂസർക്ക് നേരിട്ട് സ്ക്രീനിൽ കീ എന്റർ ചെയ്യാം
api_key_input = st.text_input("നിങ്ങളുടെ Gemini API Key (AQ...) ഇവിടെ നൽകുക:", type="password")

# എപിഐ കീ ഉണ്ടെന്ന് ഉറപ്പുവരുത്തുന്നു
api_key = api_key_input or os.environ.get("GEMINI_API_KEY")

# വോയിസ് സെലക്ഷൻ (Leda ഉൾപ്പെടെയുള്ളവ)
voice_option = st.selectbox(
    "വോയ്സ് തിരഞ്ഞെടുക്കുക:",
    ["Laomedeia (Leda - Free Voice)", "Aoede", "Puck", "Charon", "Zephyr"]
)

# ടെക്സ്റ്റ് ബോക്സ് (വലിയ ടെക്സ്റ്റുകൾ ഇവിടെ പേസ്റ്റ് ചെയ്യാം)
text_input = st.text_area("മലയാളം ടെക്സ്റ്റ് ഇവിടെ ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ പേസ്റ്റ് ചെയ്യുക:", height=250, 
                          placeholder="ഇവിടെ നിങ്ങളുടെ മലയാളം വാചകങ്ങൾ എഴുതുക...")

if st.button("Convert to Speech (വോയ്സ് ആക്കുക)"):
    if not api_key:
        st.error("ദയവായി സാധുവായ ഒരു Gemini API Key നൽകുക!")
    elif not text_input.strip():
        st.warning("ദയവായി എന്തെങ്കിലും ടെക്സ്റ്റ് ടൈപ്പ് ചെയ്യുക!")
    else:
        with st.spinner("വോയ്സ് നിർമ്മിച്ചുകൊണ്ടിരിക്കുന്നു... ദയവായി കാത്തിരിക്കുക..."):
            try:
                # പുതിയ ഔദ്യോഗിക SDK വഴി ക്ലയന്റ് ആരംഭിക്കുന്നു
                client = genai.Client(api_key=api_key)
                
                # വലിയ ടെക്സ്റ്റുകൾ കൈകാര്യം ചെയ്യാൻ തക്കവണ്ണം പ്രോംപ്റ്റ് തയ്യാറാക്കുന്നു
                # തന്നിരിക്കുന്ന മലയാളം ടെക്സ്റ്റ് മാറ്റമില്ലാതെ വായിക്കാൻ നിർദ്ദേശം നൽകുന്നു
                response = client.models.generate_content(
                    model='gemini-2.5-pro-preview-tts', # പുതിയ TTS മോഡൽ
                    contents=text_input,
                    config=types.GenerateContentConfig(
                        response_mime_type="audio/mp3", # ഓഡിയോ ഫോർമാറ്റ്
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice_option.split(" ")[0] # വോയിസ് പേര് വേർതിരിക്കുന്നു
                                )
                            )
                        )
                    )
                )
                
                # ഓഡിയോ ഡാറ്റ വിജയകരമായി ലഭിച്ചാൽ അത് പ്ലേ ചെയ്യാനും ഡൗൺലോഡ് ചെയ്യാനും നൽകുന്നു
                if response.candidates and response.candidates[0].content:
                    # ലഭിച്ച response-ൽ നിന്നും ഓഡിയോ ബൈറ്റുകൾ വേർതിരിച്ചെടുക്കുന്നു
                    audio_bytes = response.candidates[0].content.parts[0].inline_data.data
                    
                    st.success("🎉 വോയ്സ് വിജയകരമായി നിർമ്മിച്ചിരിക്കുന്നു!")
                    
                    # വെബ്സൈറ്റിൽ ഓഡിയോ പ്ലെയർ കാണിക്കുന്നു
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # ഡൗൺലോഡ് ബട്ടൺ
                    st.download_button(
                        label="📥 വോയ്സ് ഡൗൺലോഡ് ചെയ്യുക (MP3)",
                        data=audio_bytes,
                        file_name="malayalam_speech.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("ഓഡിയോ ജനറേറ്റ് ചെയ്യാൻ സാധിച്ചില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.")
                    
            except Exception as e:
                st.error(f"Error സംഭവിച്ചിരിക്കുന്നു: {str(e)}")
