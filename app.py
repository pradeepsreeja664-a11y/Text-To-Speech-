import streamlit as st
from google import genai
from google.genai import types
import base64
import os

st.set_page_config(page_title="മലയാളം Text to Speech", page_icon="🎙️", layout="centered")

st.title("🎙️ Gemini മലയാളം Text to Speech")
st.write("Gemini API ഉപയോഗിച്ച് എത്ര വലിയ മലയാളം ടെക്സ്റ്റും വോയ്സ് ആക്കി മാറ്റാം.")

# യൂസർക്ക് സ്ക്രീനിൽ കീ എന്റർ ചെയ്യാനുള്ള ബോക്സ്
api_key_input = st.text_input("നിങ്ങളുടെ Gemini API Key (AQ...) ഇവിടെ നൽകുക:", type="password")

# വോയിസ് സെലക്ഷൻ (Leda-യുടെ ഒഫീഷ്യൽ സിസ്റ്റം നെയിം Aoede എന്നാണ്)
voice_option = st.selectbox(
    "വോയ്സ് തിരഞ്ഞെടുക്കുക:",
    ["Aoede (Leda - Free Premium Voice)", "Puck", "Charon", "Zephyr"]
)

text_input = st.text_area("മലയാളം ടെക്സ്റ്റ് ഇവിടെ ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ പേസ്റ്റ് ചെയ്യുക:", height=250, 
                          placeholder="ഇവിടെ നിങ്ങളുടെ മലയാളം വാചകങ്ങൾ എഴുതുക...")

if st.button("Convert to Speech (വോയ്സ് ആക്കുക)"):
    # സ്ക്രീനിൽ കീ ഇല്ലെങ്കിൽ സിസ്റ്റം എൻവയോൺമെന്റിൽ ഉണ്ടോ എന്ന് നോക്കുന്നു
    final_key = api_key_input or os.environ.get("GEMINI_API_KEY")
    
    if not final_key:
        st.error("ദയവായി സാധുവായ ഒരു Gemini API Key നൽകുക!")
    elif not text_input.strip():
        st.warning("ദയവായി എന്തെങ്കിലും ടെക്സ്റ്റ് ടൈപ്പ് ചെയ്യുക!")
    else:
        with st.spinner("വോയ്സ് നിർമ്മിച്ചുകൊണ്ടിരിക്കുന്നു... ദയവായി കാത്തിരിക്കുക..."):
            try:
                # എൻവയോൺമെന്റ് വേരിയബിളിലേക്ക് കീ സെറ്റ് ചെയ്യുന്നു
                os.environ["GEMINI_API_KEY"] = final_key
                
                # ഗൂഗിളിന്റെ ഒഫീഷ്യൽ പുതിയ ക്ലയന്റ് കോളിംഗ്
                client = genai.Client()
                
                # സെലക്ട് ചെയ്ത വോയിസ് പേര് മാത്രം വേർതിരിച്ചെടുക്കുന്നു (ഉദാ: Aoede)
                selected_voice = voice_option.split(" ")[0]
                
                # 400 Error പരിഹരിക്കാൻ response_modalities ഉപയോഗിക്കുന്നു
                response = client.models.generate_content(
                    model='gemini-2.5-flash-preview-tts', # ശരിയായ ഒഫീഷ്യൽ TTS മോഡൽ
                    contents=f"Please read the following Malayalam text out loud accurately with no extra commentary: {text_input}",
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"], # ഇവിടെ ഓഡിയോ റെസ്പോൺസ് വേണമെന്ന് ആവശ്യപ്പെടുന്നു
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=selected_voice
                                )
                            )
                        )
                    )
                )
                
                # ഓഡിയോ കണ്ടെന്റ് റെസ്പോൺസിൽ ഉണ്ടോ എന്ന് പരിശോധിക്കുന്നു
                audio_parts = [part for part in response.candidates[0].content.parts if part.inline_data]
                
                if audio_parts:
                    # ബൈനറി ഓഡിയോ ഡാറ്റ വേർതിരിച്ചെടുക്കുന്നു
                    audio_bytes = audio_parts[0].inline_data.data
                    
                    st.success("🎉 വോയ്സ് വിജയകരമായി നിർമ്മിച്ചിരിക്കുന്നു!")
                    
                    # വെബ്സൈറ്റിൽ ഓഡിയോ പ്ലെയർ കാണിക്കുന്നു (Gemini നൽകുന്നത് WAV/PCM ഫോർമാറ്റാണ്)
                    st.audio(audio_bytes, format="audio/wav")
                    
                    # ഡൗൺലോഡ് ബട്ടൺ
                    st.download_button(
                        label="📥 വോയ്സ് ഡൗൺലോഡ് ചെയ്യുക (WAV)",
                        data=audio_bytes,
                        file_name="malayalam_speech.wav",
                        mime="audio/wav"
                    )
                else:
                    st.error("ഓഡിയോ ജനറേറ്റ് ചെയ്യാൻ സാധിച്ചില്ല. നൽകിയ ടെക്സ്റ്റ് വീണ്ടും പരിശോധിക്കുക.")
                    
            except Exception as e:
                st.error(f"Error സംഭവിച്ചിരിക്കുന്നു: {str(e)}")
