# J1MSKY Voice Pipeline Integration
## KittenTTS + Local TTS Strategy

---

## 🎯 STATUS: Forked & Ready

**KittenTTS Fork:** https://github.com/TheMindExpansionNetwork/KittenTTS
**Local Clone:** `/home/m1ndb0t/Desktop/J1MSKY-BCI/tools/KittenTTS`

---

## ⚠️ PYTHON VERSION ISSUE

**Current Pi Python:** 3.13  
**KittenTTS Requires:** Python <3.13, >=3.8  
**Issue:** Dependency `misaki` not compatible with 3.13

**Solutions:**

### Option 1: Use Pyenv (Recommended)
Install Python 3.11 alongside system Python:
```bash
curl https://pyenv.run | bash
pyenv install 3.11.9
pyenv local 3.11.9
pip install kittentts
```

### Option 2: Docker Container
Run KittenTTS in Docker with Python 3.11:
```dockerfile
FROM python:3.11-slim
RUN pip install kittentts
```

### Option 3: Use Existing TTS Skill
Current system has `sag` (ElevenLabs) and `sherpa-onnx-tts` skills.

---

## 🎙️ VOICE PIPELINE OPTIONS

### A. Cloud TTS (Current - Working)
**Skill:** `sag` (ElevenLabs)  
**Pros:** High quality, multiple voices, no Pi load  
**Cons:** Requires API key, internet dependency, costs $  
**Status:** ✅ Already working

### B. Local TTS (Target - KittenTTS)
**Model:** KittenTTS nano (15M params, 19MB)  
**Pros:** Free, offline, privacy, fast  
**Cons:** Setup complexity, Python version issue  
**Voices:** Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo  
**Status:** ⏳ Needs Python 3.11 setup

### C. Hybrid Approach (Recommended)
```python
# Try local first, fallback to cloud
try:
    from kittentts import KittenTTS
    tts = KittenTTS("KittenML/kitten-tts-nano-0.8-int8")
    audio = tts.generate(text, voice='Jasper')
except:
    # Fallback to ElevenLabs
    from skills import sag
    sag.speak(text, voice='Nova')
```

---

## 📥 MODEL DOWNLOADS

When Python 3.11 is ready, download these to Pi:

| Model | Size | Use Case |
|-------|------|----------|
| `kitten-tts-nano-int8` | 19MB | Fast, everyday use |
| `kitten-tts-micro` | 41MB | Better quality |
| `kitten-tts-mini` | 80MB | Best quality |

**Storage:** All models = ~140MB (fits on Pi)

---

## 🔧 INTEGRATION PLAN

### Phase 1: Setup Python 3.11
```bash
# Install pyenv
curl https://pyenv.run | bash
# Add to .bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
# Install Python 3.11
pyenv install 3.11.9
```

### Phase 2: Install KittenTTS
```bash
cd ~/Desktop/J1MSKY-BCI/tools/KittenTTS
pyenv local 3.11.9
pip install -e .
# Download models
python -c "from kittentts import KittenTTS; KittenTTS('KittenML/kitten-tts-nano-0.8-int8')"
```

### Phase 3: Create Voice Pipeline
```python
# j1msky_bci/voice/pipeline.py
import os
from pathlib import Path

class VoicePipeline:
    def __init__(self):
        self.local_tts = None
        self.cloud_tts = None
        self.use_local = self._check_local()
    
    def _check_local(self):
        """Check if local KittenTTS available"""
        try:
            from kittentts import KittenTTS
            self.local_tts = KittenTTS("KittenML/kitten-tts-nano-0.8-int8")
            return True
        except:
            return False
    
    def speak(self, text, voice='Jasper', priority='auto'):
        """
        Generate speech
        priority: 'local' | 'cloud' | 'auto'
        """
        if priority == 'local' and self.use_local:
            return self._local_speak(text, voice)
        elif priority == 'cloud':
            return self._cloud_speak(text)
        else:  # auto
            if self.use_local:
                return self._local_speak(text, voice)
            else:
                return self._cloud_speak(text)
    
    def _local_speak(self, text, voice):
        """Use KittenTTS"""
        audio = self.local_tts.generate(text, voice=voice)
        # Play via Pi audio (Echo/Alexa)
        return audio
    
    def _cloud_speak(self, text):
        """Fallback to ElevenLabs"""
        from skills import sag
        sag.speak(text)
```

### Phase 4: Agent Voice Integration
```python
# Each agent gets a voice
AGENT_VOICES = {
    'opus': 'Bella',      # CEO - professional female
    'sonnet': 'Jasper',   # Ops - calm male
    'kimi': 'Luna',       # Dev - energetic female
    'minimax': 'Bruno',   # Fast - energetic male
    'codex': 'Rosie',     # Specialist - warm female
}

def agent_speak(agent, message):
    voice = AGENT_VOICES.get(agent, 'Jasper')
    pipeline.speak(f"[{agent}] {message}", voice=voice)
```

---

## 🎨 USE CASES

### 1. Agent Announcements
- Agents speak status updates
- "SCOUT: News gathered"
- "VITALS: Temperature normal"
- Different voice per agent

### 2. Brain-Art Descriptions
- Describe generated art
- "Creating surreal landscape from your theta waves"
- Guide user through experience

### 3. Sleep Mode Narration
- Gentle voice during sleep art
- "Entering REM sleep, generating dreamscape"
- Whisper mode for night

### 4. Interactive Feedback
- Real-time coaching
- "Relax more to create softer colors"
- "Focus to sharpen the image"

---

## 💾 STORAGE PLAN

**Models on Pi:**
```
~/models/
├── kittentts/
│   ├── nano-int8/     # 19MB - Default
│   ├── micro/         # 41MB - Quality mode
│   └── mini/          # 80MB - Best quality
└── voices/
    └── [downloaded voices]
```

**Total:** ~140MB (plenty of space on Pi)

---

## ⏱️ NEXT STEPS

1. **Setup Python 3.11** (15 min)
2. **Install KittenTTS** (5 min)
3. **Download nano-int8 model** (2 min)
4. **Test voice generation** (5 min)
5. **Integrate with agents** (30 min)

**Total:** ~1 hour setup

---

## 🔄 ALTERNATIVE: Use sherpa-onnx-tts (Already Installed)

If KittenTTS setup is delayed, use existing skill:
```python
from skills import sherpa_onnx_tts
sherpa_onnx_tts.speak("Hello from J1MSKY", voice='en-US')
```

**Pros:** Already working, no setup  
**Cons:** Lower quality than KittenTTS

---

*Document Created: February 19, 2026*  
*Status: Forked, ready for Python 3.11 setup*  
*Priority: Medium (cloud TTS working meanwhile)*
