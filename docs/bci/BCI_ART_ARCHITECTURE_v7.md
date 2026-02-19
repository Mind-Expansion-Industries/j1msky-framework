# ◈ J1MSKY BCI-ART SYSTEM v7.0 ARCHITECTURE ◈
## Multi-Modal Biofeedback AI Art Generation Platform

---

## 🎯 EXECUTIVE SUMMARY

**Mission:** Build a real-time brain-computer interface (BCI) system that transforms EEG (brain) and HRV (heart) signals into AI-generated art and music.

**Key Innovation:** Multi-modal biofeedback (brain + heart) with autonomous sleep-art generation.

**Tech Stack:**
- **Brain:** Emotiv EPOC X + ZUNA EEG Foundation Model
- **Heart:** Polar H10 + BLE SDK
- **Art:** ComfyUI + Modal.com cloud GPU
- **Distribution:** OSC to Ableton Live, VJ software, visual engines

---

## 🏗️ REPOSITORY STRUCTURE (3 Repos)

### Repo 1: `j1msky-bci-tools` (Hardware Interface Layer)
**Purpose:** All BCI hardware connections and signal processing

```
j1msky-bci-tools/
├── emotiv/
│   ├── __init__.py
│   ├── cortex_client.py          # Official Emotiv Cortex API
│   ├── emokit_bridge.py          # Open-source emokit fallback
│   ├── python_emotiv_wrapper.py  # Community python-emotiv
│   ├── cykit_interface.py        # CyKit Windows/Linux bridge
│   └── zuna_processor.py         # ZUNA EEG model integration
│
├── polar/
│   ├── __init__.py
│   ├── polar_ble.py              # Polar BLE SDK wrapper
│   ├── bleakheart_wrapper.py     # Cross-platform BLE
│   └── hrv_processor.py          # Heart rate variability analysis
│
├── fusion/
│   ├── __init__.py
│   ├── multimodal_fusion.py      # Brain + Heart signal fusion
│   ├── state_detector.py         # Detect focus/calm/creative states
│   └── sleep_classifier.py       # REM/deep/sleep-wake detection
│
├── osc/
│   ├── __init__.py
│   ├── osc_server.py             # Receive commands
│   ├── osc_client.py             # Send to ComfyUI, Ableton, etc.
│   └── osc_router.py             # Route signals to multiple outputs
│
├── api/
│   ├── __init__.py
│   ├── modal_comfyui.py          # Modal.com ComfyUI deployment
│   ├── local_comfyui.py          # Local GPU option
│   └── art_generator.py          # High-level art generation API
│
├── config/
│   ├── hardware.yaml             # Hardware settings
│   ├── osc.yaml                  # OSC routing config
│   └── modal.yaml                # Modal.com credentials
│
├── tests/
│   ├── test_emotiv.py
│   ├── test_polar.py
│   └── test_fusion.py
│
├── requirements.txt
├── setup.py
└── README.md
```

**Agent Ownership:** Kimi (Lead) + MiniMax (Implementation)

---

### Repo 2: `j1msky-bci-docs` (Documentation & Research)
**Purpose:** Complete documentation, protocols, research findings

```
j1msky-bci-docs/
├── research/
│   ├── zuna_paper.md             # ZUNA model analysis
│   ├── emotiv_sdk_comparison.md  # Compare Cortex vs Emokit vs CyKit
│   ├── polar_hrv_guide.md        # HRV interpretation
│   ├── osc_protocols.md          # OSC message specifications
│   └── art_generation_methods.md # AI art techniques
│
├── protocols/
│   ├── eeg_to_osc_mapping.md     # Channel → OSC address mapping
│   ├── heart_to_osc_mapping.md   # BPM/HRV → OSC mapping
│   ├── state_definitions.md      # What is "focused" vs "creative"
│   ├── sleep_stages.md           # EEG signatures for sleep stages
│   └── ableton_integration.md    # Ableton Live OSC setup
│
├── tutorials/
│   ├── hardware_setup.md         # EPOC X + Polar setup guide
│   ├── first_brain_art.md        # Hello world brain art
│   ├── sleep_art_generation.md   # Autonomous sleep mode
│   ├── live_vj_performance.md    # Real-time performance guide
│   └── mobile_app_setup.md       # Phone app for heart monitor
│
├── api/
│   ├── api_reference.md          # REST API docs
│   ├── osc_reference.md          # OSC message reference
│   └── python_sdk.md             # Python library docs
│
├── papers/
│   └── ( academic papers on EEG art, neurofeedback )
│
├── LICENSE
└── README.md
```

**Agent Ownership:** Sonnet (Documentation) + Opus (Research direction)

---

### Repo 3: `j1msky-bci-mobile` (Mobile Companion App)
**Purpose:** Phone app for Polar HRM when not wearing EPOC X

```
j1msky-bci-mobile/
├── android/
│   └── (Android Studio project)
├── ios/
│   └── (Xcode project)
├── shared/
│   ├── polar_ble.dart            # Cross-platform BLE
│   ├── osc_client.dart           # Send to Pi
│   └── hrv_calculator.dart       # Real-time HRV
├── docs/
│   └── flutter_setup.md
└── README.md
```

**Agent Ownership:** MiniMax (Fast prototyping) + Sonnet (UI/UX)
**Status:** Future phase (after core system working)

---

## 🧠 SYSTEM ARCHITECTURE

### Layer 1: Hardware Acquisition
```
┌─────────────────────────────────────────────────────────────┐
│  HARDWARE LAYER                                              │
├─────────────────────────────────────────────────────────────┤
│  Emotiv EPOC X (14ch EEG)        Polar H10 (HRV)            │
│        ↓                               ↓                    │
│  Cortex API / Emokit / CyKit      Polar BLE SDK             │
│        ↓                               ↓                    │
│  Raw EEG (256Hz)                  Raw ECG (130Hz)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
```

### Layer 2: Signal Processing (ZUNA + Fusion)
```
┌─────────────────────────────────────────────────────────────┐
│  SIGNAL PROCESSING LAYER                                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  EEG Pipeline:                                               │
│  Raw EEG → ZUNA Model → Denoised → Band Decomposition        │
│  (256Hz)    (380M param)        (Alpha/Beta/Theta/Delta)    │
│                                                              │
│  Heart Pipeline:                                             │
│  Raw ECG → R-Peak Detection → BPM → HRV Analysis             │
│  (130Hz)   (Pan-Tompkins)    (RMSSD/SDNN)                   │
│                                                              │
│  Fusion:                                                     │
│  EEG State + HRV State = Multi-Modal State                   │
│  (Focus/Relax/Creative/Sleep)                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
```

### Layer 3: OSC Distribution
```
┌─────────────────────────────────────────────────────────────┐
│  OSC ROUTING LAYER                                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /bci/eeg/alpha        → 0.0-1.0 (Alpha power)              │
│  /bci/eeg/beta         → 0.0-1.0 (Beta power)               │
│  /bci/eeg/theta        → 0.0-1.0 (Theta power)              │
│  /bci/eeg/delta        → 0.0-1.0 (Delta power)              │
│  /bci/eeg/gamma        → 0.0-1.0 (Gamma power)              │
│  /bci/eeg/focus        → 0-100 (Focus score)                │
│  /bci/eeg/relax        → 0-100 (Relax score)                │
│  /bci/eeg/creative     → 0-100 (Creative state)             │
│  /bci/eeg/sleep_stage  → awake/light/deep/rem               │
│                                                              │
│  /bci/heart/bpm        → 40-200 (Beats per minute)          │
│  /bci/heart/hrv        → 0-100 (HRV coherence)              │
│  /bci/heart/rmssd      → ms (HRV metric)                    │
│  /bci/heart/sdnn       → ms (HRV metric)                    │
│                                                              │
│  /bci/fusion/state     → calm/focused/creative/excited      │
│  /bci/fusion/intensity → 0.0-1.0 (Overall activation)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
```

### Layer 4: Art Generation (Modal + ComfyUI)
```
┌─────────────────────────────────────────────────────────────┐
│  ART GENERATION LAYER                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Real-Time Mode:                                             │
│  OSC Messages → ComfyUI Workflow → Modal GPU → Image         │
│  (50ms latency)                                              │
│                                                              │
│  Workflow Nodes:                                             │
│  - KSampler (diffusion)                                      │
│  - ControlNet (EEG-guided)                                   │
│  - IPAdapter (style transfer)                                │
│  - AnimateDiff (temporal for video)                          │
│                                                              │
│  Sleep Mode:                                                 │
│  EEG Classifier detects sleep stage → Auto-trigger art       │
│  - REM → Surreal dreamscapes                                 │
│  - Deep → Abstract cosmic visuals                            │
│  - Light → Soft flowing patterns                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
```

### Layer 5: Output Distribution
```
┌─────────────────────────────────────────────────────────────┐
│  OUTPUT LAYER                                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Visual Outputs:                                             │
│  - ComfyUI Preview (real-time)                               │
│  - Resolume Arena (VJ software via OSC)                      │
│  - TouchDesigner (generative visuals)                        │
│  - LED strips (via ESP32 + ArtNet)                           │
│                                                              │
│  Audio Outputs:                                              │
│  - Ableton Live (OSC control of synths/effects)              │
│  - MaxMSP (generative audio)                                 │
│  - Pure Data (open source alternative)                       │
│                                                              │
│  Recording:                                                  │
│  - Auto-save all generated art                               │
│  - Timestamp with EEG signature                              │
│  - Upload to gallery (optional)                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 UNIQUE FEATURES

### 1. Multi-Modal Biofeedback
- **Brain + Heart fusion** (most BCI only uses EEG)
- HRV adds emotional/calm dimension
- More nuanced art generation

### 2. Sleep Art Generation
- **Autonomous mode while sleeping**
- Detects REM, deep, light sleep
- Creates dream-inspired art
- Wake up to gallery of sleep art

### 3. Agent Orchestration via Brain
- **Train agents with brain states**
- Focus = Kimi (coding tasks)
- Creative = Sonnet (content tasks)
- Relaxed = Auto-backup/maintenance

### 4. Real-Time VJ Performance
- **Live brain-controlled visuals**
- For performances, meditation, therapy
- OSC to any VJ software

### 5. No API Dependencies
- All open source (ZUNA, ComfyUI, Emokit)
- Only Modal.com for GPU (can self-host)
- Polar SDK is free

---

## 💰 MONETIZATION PATH

### Phase 1: Personal Use (Now)
- Build for yourself
- Create sleep art gallery
- Document process

### Phase 2: Content Creation (3 months)
- YouTube/Twitch streams of brain art
- NFTs of unique pieces
- "Art by my mind" brand

### Phase 3: Tools Release (6 months)
- Open source the repos
- Paid presets/workflows
- Consulting for installations

### Phase 4: Product (12 months)
- Pre-configured Pi + Software kit
- $999 hardware + $49/month software
- B2B: Wellness centers, artists, researchers

---

## 📋 IMPLEMENTATION ROADMAP

### Week 1: Foundation
- [ ] Fork all 5 GitHub repos
- [ ] Set up `j1msky-bci-tools` structure
- [ ] Test Emotiv connection (Cortex API)
- [ ] Test Polar H10 connection

### Week 2: Signal Processing
- [ ] Integrate ZUNA model
- [ ] Build EEG band decomposition
- [ ] Build HRV analysis
- [ ] Create fusion algorithm

### Week 3: OSC + Art
- [ ] Build OSC router
- [ ] Deploy ComfyUI on Modal
- [ ] Create first brain→art pipeline
- [ ] Test with Ableton Live

### Week 4: Polish
- [ ] Build sleep detection
- [ ] Create autonomous mode
- [ ] Documentation
- [ ] First public demo

---

## 🚀 AGENT TASK ASSIGNMENTS

### Kimi (Lead Developer)
- Architecture design
- ZUNA integration
- Modal.com deployment
- Code review

### MiniMax (Fast Implementation)
- Emotiv SDK wrappers
- Polar BLE connection
- OSC routing
- Testing scripts

### Sonnet (Documentation & UX)
- API documentation
- User guides
- Workflow design
- Integration testing

### Opus (Strategic Architecture)
- System design decisions
- Research direction
- Complex algorithm design
- Final review

### Codex (Specialist)
- ComfyUI custom nodes
- Modal.com optimization
- API integrations

---

## 🔗 CRITICAL LINKS

**GitHub Repos to Fork:**
1. https://github.com/Zyphra/zuna (ZUNA EEG model)
2. https://github.com/Comfy-Org/ComfyUI (AI art)
3. https://github.com/bibeks/emotiv-community-sdk (Emotiv)
4. https://github.com/openyou/emokit (Open Emotiv)
5. https://github.com/ozancaglayan/python-emotiv (Python Emotiv)
6. https://github.com/CymatiCorp/CyKit (CyKit bridge)
7. https://github.com/polarofficial/polar-ble-sdk (Polar)
8. https://github.com/fsmeraldi/bleakheart (BLE HRV)

**Modal.com:**
- https://modal.com/docs/examples/comfyapp (Deployment template)

---

## ✅ SUCCESS CRITERIA

- [ ] EEG streaming at 256Hz
- [ ] Heart rate at 1Hz with HRV
- [ ] Art generation < 2 seconds
- [ ] Sleep stage detection > 80% accuracy
- [ ] 6+ hour autonomous operation
- [ ] Zero API dependencies (except Modal GPU)

---

**Ready to execute. Send command to begin forking and building.** 🧠🎨

*Architecture by Claude Opus (CEO)*  
*Implementation plan for agentic teams*  
*Version: 7.0 - Multi-Modal BCI Art System*