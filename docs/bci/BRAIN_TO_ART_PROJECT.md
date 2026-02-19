# ◈ J1MSKY BRAIN-TO-ART PROJECT ◈
## Emotiv Epoch X Integration Roadmap

---

## 🎯 PROJECT VISION

**Goal:** Create art directly from brain signals using Emotiv Epoch X BCI headset

**Pipeline:**
```
Brain Signals (EEG)
    ↓
Emotiv Epoch X Headset
    ↓
Cortex API (Emotiv SDK)
    ↓
Raspberry Pi Processing
    ↓
OSC (Open Sound Control)
    ↓
AI Art Generation
    ↓
Visual/Music Output
```

---

## 🧠 EMOTIV EPOCH X INTEGRATION

### Hardware
- **Device:** Emotiv Epoch X (Developer Edition)
- **Sensors:** 14-channel EEG + 2 reference channels
- **Data:** Raw EEG, Performance Metrics, Motion Data
- **Connection:** Bluetooth to Raspberry Pi

### SDK/API Options
1. **Cortex API** (Official Emotiv)
   - WebSocket-based
   - Real-time brain data
   - Python SDK available
   - URL: https://emotiv.gitbook.io/cortex-api

2. **Python-Emotiv** (Community)
   - Linux-compatible
   - Direct headset access
   - GitHub: ozancaglayan/python-emotiv

---

## 📊 BRAIN DATA TO ART MAPPING

### EEG Bands → Art Parameters

| Brain Wave | Frequency | Artistic Mapping |
|------------|-----------|------------------|
| **Delta** | 0.5-4 Hz | Color depth, background layers |
| **Theta** | 4-8 Hz | Brush stroke size, texture |
| **Alpha** | 8-13 Hz | Color palette selection |
| **Beta** | 13-30 Hz | Line intensity, motion speed |
| **Gamma** | 30-100 Hz | Detail level, complexity |

### Mental States → Art Styles

| State | EEG Signature | Art Output |
|-------|---------------|------------|
| **Relaxed** | High Alpha | Soft, flowing, pastel |
| **Focused** | High Beta | Sharp, geometric, structured |
| **Creative** | Theta bursts | Abstract, surreal, colorful |
| **Excited** | High Gamma | Intense, vibrant, dynamic |
| **Meditative** | High Delta | Minimal, deep, cosmic |

---

## 🔌 OSC INTEGRATION

### What is OSC?
- **Open Sound Control**
- Protocol for communication between devices
- Perfect for real-time brain data streaming
- Used by musicians, artists, VJs

### Raspberry Pi as OSC Bridge
```python
# Pi receives EEG from Emotiv
# Pi sends OSC to art software
# Pi can also receive OSC for feedback
```

### OSC Message Structure
```
/brain/eeg/alpha     → Alpha wave value (0.0-1.0)
/brain/eeg/beta      → Beta wave value
/brain/eeg/theta     → Theta wave value
/brain/eeg/gamma     → Gamma wave value
/brain/state/focus   → Focus level (0-100)
/brain/state/relax   → Relaxation level
/brain/art/trigger   → Trigger art generation
```

---

## 🎨 ART GENERATION WORKFLOWS

### Workflow 1: Real-Time Brain Painting
```
1. User wears Epoch X
2. Pi streams EEG via OSC
3. Stable Diffusion/AI receives brain parameters
4. Image generated in real-time
5. Display updates continuously
```

### Workflow 2: Brain-State Triggered Art
```
1. Detect state changes (focus→relax)
2. Trigger art generation on state shift
3. Save artwork with brain signature
4. Build gallery of mental states
```

### Workflow 3: Neurofeedback Training
```
1. Target specific brain state
2. Visual feedback (art evolves with brain)
3. Train user to control art with mind
4. Gamified meditation/creativity training
```

---

## 🛠️ TECHNICAL ARCHITECTURE

### Software Stack
```
Layer 1: Emotiv Cortex SDK
    ↓
Layer 2: Python Brain Processor (Pi)
    ↓
Layer 3: OSC Server/Client
    ↓
Layer 4: AI Art Generator
    ↓
Layer 5: Display/Output
```

### Required Libraries
```python
# EEG Processing
pip install cortex-api          # Emotiv official
pip install pyemotiv            # Community alternative

# OSC Communication
pip install python-osc          # OSC server/client

# AI Art Generation
pip install replicate           # For Stable Diffusion
pip install openai              # DALL-E option

# Visualization
pip install pygame              # Real-time display
pip install opencv-python       # Video processing
```

---

## 📁 PROJECT STRUCTURE

```
J1MSKY/brain-art/
├── cortex/
│   ├── __init__.py
│   ├── client.py              # Connect to Emotiv
│   ├── stream.py              # EEG data stream
│   └── parser.py              # Parse brain data
├── osc/
│   ├── __init__.py
│   ├── server.py              # Receive OSC
│   ├── client.py              # Send OSC
│   └── mapper.py              # EEG → OSC mapping
├── art/
│   ├── __init__.py
│   ├── generator.py           # AI art generation
│   ├── style.py               # Style presets
│   └── canvas.py              # Real-time canvas
├── models/
│   └── brain-art-model.pkl    # Fine-tuned model
├── config/
│   └── brain-art.json         # Settings
├── tests/
│   └── test_cortex.py
└── main.py                    # Entry point
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Basic Connection (Week 1)
- [ ] Connect Epoch X to Pi via Bluetooth
- [ ] Install Cortex SDK
- [ ] Stream raw EEG data
- [ ] Print brain wave values

### Phase 2: OSC Bridge (Week 2)
- [ ] Create OSC server on Pi
- [ ] Map EEG to OSC messages
- [ ] Test with OSC receiver (TouchDesigner/MaxMSP)
- [ ] Document protocol

### Phase 3: Art Generation (Week 3)
- [ ] Connect to Stable Diffusion API
- [ ] Map brain waves to prompts
- [ ] Generate first brain-art piece
- [ ] Real-time vs triggered modes

### Phase 4: Fine-Tuning (Week 4)
- [ ] Collect brain-art dataset
- [ ] Fine-tune small model on Pi
- [ ] Personal brain → art mapping
- [ ] Optimize latency

### Phase 5: Integration (Week 5-6)
- [ ] Merge with J1MSKY Agency
- [ ] Add to dashboard
- [ ] Monetization options
- [ ] Documentation

---

## 💰 MONETIZATION IDEAS

### 1. Brain-Art NFTs
- Unique art generated from user's brain
- Mint as NFTs
- Price: $50-500 per piece

### 2. Neurofeedback Sessions
- Guided meditation with visual feedback
- Subscription: $20/month
- Corporate wellness packages

### 3. Live Performances
- Brain-controlled VJ sets
- Art galleries with live brain painting
- Event bookings: $500-2000/show

### 4. Hardware + Software Kit
- Pre-configured Pi + Emotiv bundle
- Custom software
- Price: $999 (hardware + software)

---

## 🔗 COMPATIBILITY CHECKLIST

### Emotiv Epoch X on Pi
- [ ] Bluetooth pairing works
- [ ] Cortex SDK runs on ARM64
- [ ] Python 3.11+ compatibility
- [ ] 8GB RAM sufficient for processing

### OSC Compatibility
- [ ] python-osc works on Pi
- [ ] Low latency (< 50ms)
- [ ] Can interface with MaxMSP, TouchDesigner, Resolume

### AI Art on Pi
- [ ] Replicate API (cloud-based)
- [ ] OR: Local Stable Diffusion (slow but possible)
- [ ] Fine-tuning: Use cloud, not local

---

## 📚 RESOURCES

### Official Documentation
- Cortex API: https://emotiv.gitbook.io/cortex-api
- Emotiv Developer: https://www.emotiv.com/pages/developer

### GitHub Repos
- python-emotiv: https://github.com/ozancaglayan/python-emotiv
- EEGsynth: https://www.eegsynth.org
- PiEEG: https://www.crowdsupply.com/hackerbci/pieeg

### OSC Tools
- python-osc: https://pypi.org/project/python-osc/
- TouchDesigner: https://derivative.ca/
- MaxMSP: https://cycling74.com/

---

## 🎯 NEXT STEPS

1. **Confirm GitHub repo** you want me to look at
2. **Test basic connection** - Pi ↔ Epoch X
3. **Set up Cortex SDK** on Pi
4. **Create OSC bridge** proof of concept
5. **Generate first brain-art**

**Ready when you are! Send me the GitHub repo link.** 🧠🎨

---

*Document Created: February 19, 2026*  
*Status: Planning Phase*  
*Integration Target: J1MSKY Agency v6.0*
