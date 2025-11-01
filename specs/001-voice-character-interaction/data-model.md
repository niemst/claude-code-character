# Data Model: Voice-Enabled Character Interaction

**Feature**: Voice-Enabled Character Interaction for Claude Code
**Date**: 2025-11-01
**Source**: Extracted from [spec.md](./spec.md) Key Entities section

## Overview

This document defines the data structures for voice configuration, character profiles, and voice session state. All entities are stored as JSON and managed in-memory during runtime.

---

## Entity: VoiceConfiguration

**Purpose**: User preferences for voice input/output settings

**Storage Location**: `~/.claude-code/voice-config.json`

**Schema**:

```typescript
interface VoiceConfiguration {
  voiceInputEnabled: boolean;
  voiceOutputEnabled: boolean;
  selectedCharacter: string | null;
  pushToTalkKey: string;
  audioDevices: {
    inputDevice: string | null;
    outputDevice: string | null;
  };
  apiKeys: {
    openai: string;
    elevenlabs: string;
  };
  sttConfig: {
    whisperModel: 'whisper-1';
  };
  ttsConfig: {
    provider: 'system' | 'elevenlabs';
    elevenlabsModel?: 'eleven_multilingual_v2' | 'eleven_turbo_v2';
    systemVoice?: string;
  };
  performance: {
    maxTranscriptionWaitSeconds: number;
    ttsStreamingEnabled: boolean;
  };
}
```

**Field Descriptions**:

| Field | Type | Description | Default Value | Validation Rules |
|-------|------|-------------|---------------|------------------|
| `voiceInputEnabled` | boolean | Whether voice input (STT) is active | `false` | None |
| `voiceOutputEnabled` | boolean | Whether voice output (TTS) is active | `false` | None |
| `selectedCharacter` | string \| null | Name of active character profile or null for no character | `null` | Must match existing character profile name or be null |
| `pushToTalkKey` | string | Keyboard shortcut for push-to-talk activation | `"Ctrl+Space"` | Valid iohook key combination |
| `audioDevices.inputDevice` | string \| null | Microphone device identifier or null for system default | `null` | Must match available audio input device |
| `audioDevices.outputDevice` | string \| null | Speaker/headphone device identifier or null for system default | `null` | Must match available audio output device |
| `apiKeys.openai` | string | OpenAI API key for Whisper STT | `""` | Non-empty string |
| `apiKeys.elevenlabs` | string | ElevenLabs API key for TTS | `""` | Non-empty string |
| `sttConfig.whisperModel` | string | Whisper model identifier | `"whisper-1"` | Must be valid OpenAI Whisper model |
| `ttsConfig.provider` | string | TTS service provider | `"system"` | Must be `"system"` or `"elevenlabs"` |
| `ttsConfig.elevenlabsModel` | string (optional) | ElevenLabs TTS model (multilingual or turbo) | `"eleven_multilingual_v2"` | Must be valid ElevenLabs model (required if provider is elevenlabs) |
| `ttsConfig.systemVoice` | string (optional) | System voice name (platform-specific) | null (uses default) | Platform-specific voice identifier (e.g., "Microsoft David" on Windows) |
| `performance.maxTranscriptionWaitSeconds` | number | Maximum wait time for STT response before timeout | `3` | Positive integer, max 10 |
| `performance.ttsStreamingEnabled` | boolean | Whether to stream TTS audio (play while receiving) | `true` | None |

**Relationships**: None (root configuration entity)

**State Transitions**:
- Configuration can be updated at any time
- Changes to `voiceInputEnabled` or `voiceOutputEnabled` take effect immediately
- Changes to `selectedCharacter` apply to next voice output
- Changes to audio devices require reinitialization of audio streams

---

## Entity: CharacterProfile

**Purpose**: Definition of a character's speaking style, personality traits, and voice characteristics

**Storage Location**: `src/character/profiles/{characterName}.json` (bundled with application)

**Schema**:

```typescript
interface CharacterProfile {
  name: string;
  displayName: string;
  description: string;
  voiceId: string;
  voiceSettings: {
    stability: number;
    similarityBoost: number;
    style?: number;
    useSpeakerBoost?: boolean;
  };
  systemPrompt: string;
  characteristicPhrases: string[];
  transformationRules: {
    addGreeting: boolean;
    useCharacteristicPhrases: boolean;
    preserveTechnicalContent: boolean;
  };
}
```

**Field Descriptions**:

| Field | Type | Description | Validation Rules |
|-------|------|-------------|------------------|
| `name` | string | Unique identifier for character (lowercase, no spaces) | Matches `/^[a-z0-9-]+$/` |
| `displayName` | string | Human-readable character name | Non-empty string |
| `description` | string | Brief description of character personality | Non-empty string |
| `voiceId` | string | ElevenLabs voice ID for this character | Valid ElevenLabs voice ID (e.g., "21m00Tcm4TlvDq8ikWAM") |
| `voiceSettings.stability` | number | Voice stability (0-1, lower = more variable/expressive) | 0.0 to 1.0 |
| `voiceSettings.similarityBoost` | number | Voice similarity boost (0-1, higher = closer to original voice) | 0.0 to 1.0 |
| `voiceSettings.style` | number (optional) | Style exaggeration (0-1, if supported by model) | 0.0 to 1.0 |
| `voiceSettings.useSpeakerBoost` | boolean (optional) | Enable speaker boost for clarity | true or false |
| `systemPrompt` | string | Instructions for LLM to transform text in character style | Non-empty string, max 500 chars |
| `characteristicPhrases` | string[] | Array of phrases character uses frequently | Array with 3-10 phrases |
| `transformationRules.addGreeting` | boolean | Whether to add character greetings to responses | None |
| `transformationRules.useCharacteristicPhrases` | boolean | Whether to inject characteristic phrases | None |
| `transformationRules.preserveTechnicalContent` | boolean | MUST be true: preserve code, paths, errors verbatim | Must be `true` (enforced) |

**Example - Toudie Profile**:

```json
{
  "name": "toudie",
  "displayName": "Toudie from Gummy Bears",
  "description": "Cheerful, helpful Gummi Bear from Gummi Glen. Enthusiastic and occasionally references Gummi Berry juice or adventures.",
  "voiceId": "21m00Tcm4TlvDq8ikWAM",
  "voiceSettings": {
    "stability": 0.5,
    "similarityBoost": 0.75,
    "style": 0.6,
    "useSpeakerBoost": true
  },
  "systemPrompt": "Transform responses to sound like Toudie from Gummy Bears: cheerful, helpful, occasionally references Gummi Berry juice or adventures. Add personality but keep all technical content (code, file paths, error messages) completely intact and unchanged.",
  "characteristicPhrases": [
    "Great gobs of gummiberries!",
    "Bouncing bears!",
    "Let me check the Gummi archives...",
    "By Gummi!",
    "This reminds me of an adventure in Gummi Glen..."
  ],
  "transformationRules": {
    "addGreeting": true,
    "useCharacteristicPhrases": true,
    "preserveTechnicalContent": true
  }
}
```

**Relationships**:
- Referenced by `VoiceConfiguration.selectedCharacter`

**State Transitions**:
- Character profiles are immutable at runtime (loaded once on startup)
- Users can switch between characters by updating `VoiceConfiguration.selectedCharacter`
- New characters can be added by creating new JSON files (requires application restart)

---

## Entity: VoiceSession

**Purpose**: Active voice interaction state during runtime

**Storage Location**: In-memory only (not persisted)

**Schema**:

```typescript
interface VoiceSession {
  sessionId: string;
  isListening: boolean;
  isPlaying: boolean;
  currentAudioStream: AudioStream | null;
  pendingResponses: Array<{
    text: string;
    timestamp: number;
    characterTransformed: boolean;
  }>;
  lastCommand: {
    spokenText: string;
    transcribedText: string;
    timestamp: number;
    transcriptionDurationMs: number;
  } | null;
  statistics: {
    commandsIssuedCount: number;
    averageTranscriptionTimeMs: number;
    averagePlaybackStartTimeMs: number;
    interruptionsCount: number;
  };
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | string | Unique identifier for this voice session (UUID) |
| `isListening` | boolean | Whether push-to-talk is currently active and capturing audio |
| `isPlaying` | boolean | Whether TTS audio is currently playing |
| `currentAudioStream` | AudioStream \| null | Active audio playback stream or null if not playing |
| `pendingResponses` | Array | Queue of responses waiting to be spoken (processed FIFO) |
| `pendingResponses[].text` | string | Response text to be spoken |
| `pendingResponses[].timestamp` | number | When response was queued (milliseconds since epoch) |
| `pendingResponses[].characterTransformed` | boolean | Whether character transformation has been applied |
| `lastCommand.spokenText` | string | Original audio as text (for debugging) |
| `lastCommand.transcribedText` | string | Final text sent to Claude Code |
| `lastCommand.timestamp` | number | When command was captured |
| `lastCommand.transcriptionDurationMs` | number | How long STT took (for performance monitoring) |
| `statistics.commandsIssuedCount` | number | Total voice commands in this session |
| `statistics.averageTranscriptionTimeMs` | number | Rolling average of STT latency |
| `statistics.averagePlaybackStartTimeMs` | number | Rolling average of TTS start latency |
| `statistics.interruptionsCount` | number | How many times user interrupted playback |

**Relationships**:
- Reads from `VoiceConfiguration` to determine behavior
- Loads `CharacterProfile` if character is active

**State Transitions**:

```
[Idle]
  → (push-to-talk pressed) → [Listening]

[Listening]
  → (push-to-talk released) → [Transcribing] → (STT complete) → [Processing Command]

[Processing Command]
  → (Claude Code generates response) → [Transforming Text] → (if character active) → [Character Applied]
  → (character not active OR character transform complete) → [Generating Audio]

[Generating Audio]
  → (TTS starts streaming) → [Playing]

[Playing]
  → (audio complete) → [Idle]
  → (user presses push-to-talk) → [Interrupted] → stop audio → [Listening]
  → (new response queued) → queue response → continue playing current
```

**Lifecycle**:
- Created when voice features enabled
- Destroyed when voice features disabled
- Persists across multiple commands within same session
- Statistics reset on session restart

---

## Validation Rules Summary

### Cross-Entity Validation

1. **Character Consistency**: `VoiceConfiguration.selectedCharacter` must match an existing `CharacterProfile.name` or be `null`
2. **Voice ID Usage**: If character is selected, `CharacterProfile.voiceId` is used for ElevenLabs TTS
3. **Technical Content Preservation**: All `CharacterProfile.transformationRules.preserveTechnicalContent` must be `true` (enforced at load time)

### Runtime Constraints

1. **Mutual Exclusion**: `VoiceSession.isListening` and `VoiceSession.isPlaying` cannot both be `true` simultaneously
2. **Audio Device Availability**: If `VoiceConfiguration.audioDevices.inputDevice` or `outputDevice` is non-null, device must be present or fallback to null (system default)
3. **API Keys Conditional**:
   - **STT**: No API key required for Web Speech API (primary). `apiKeys.openai` only required if Whisper fallback needed
   - **TTS**: No API key required if `ttsConfig.provider` is `"system"`. `apiKeys.elevenlabs` only required if `ttsConfig.provider` is `"elevenlabs"`
   - **Automatic fallback**: If `ttsConfig.provider` is `"elevenlabs"` but `apiKeys.elevenlabs` is empty, automatically fallback to `"system"` provider
4. **Provider Selection Logic**:
   - Check `apiKeys.elevenlabs`: if present and non-empty → use `"elevenlabs"` provider
   - Otherwise → use `"system"` provider
   - User can explicitly set `ttsConfig.provider` to override automatic detection

---

## Example Data Flow

### User Issues Voice Command with Toudie Character Active

1. **Configuration Loaded**:
   ```json
   {
     "voiceInputEnabled": true,
     "voiceOutputEnabled": true,
     "selectedCharacter": "toudie",
     "pushToTalkKey": "Ctrl+Space",
     "apiKeys": {
       "openai": "sk-...",
       "elevenlabs": "el_..."
     }
   }
   ```

2. **Character Profile Loaded**:
   ```json
   {
     "name": "toudie",
     "voiceId": "21m00Tcm4TlvDq8ikWAM",
     "voiceSettings": {
       "stability": 0.5,
       "similarityBoost": 0.75
     },
     "characteristicPhrases": ["Great gobs of gummiberries!", ...]
   }
   ```

3. **Session State During Command**:
   ```json
   {
     "isListening": true,
     "isPlaying": false,
     "lastCommand": null
   }
   ```

4. **After Transcription**:
   ```json
   {
     "isListening": false,
     "lastCommand": {
       "spokenText": "read file main.ts",
       "transcribedText": "read file main.ts",
       "transcriptionDurationMs": 1247
     }
   }
   ```

5. **Response Queued**:
   ```json
   {
     "pendingResponses": [
       {
         "text": "Great gobs of gummiberries! File main.ts read successfully, friend! It contains 247 lines of TypeScript code.",
         "characterTransformed": true
       }
     ]
   }
   ```

6. **During Playback**:
   ```json
   {
     "isPlaying": true,
     "currentAudioStream": { ... },
     "pendingResponses": []
   }
   ```

Note: Actual technical content ("main.ts", "247 lines", "TypeScript code") preserved verbatim, personality added around it.

---

## Storage and Persistence

### User Configuration (`~/.claude-code/voice-config.json`)
- **Created**: On first voice feature enable
- **Updated**: Whenever user changes settings
- **Format**: Pretty-printed JSON (human-readable)
- **Permissions**: User read/write only (chmod 600 on Unix systems)

### Character Profiles (`src/character/profiles/*.json`)
- **Created**: At build time (bundled with application)
- **Updated**: Only through application updates
- **Format**: Pretty-printed JSON
- **Permissions**: Read-only for users

### Voice Session (in-memory)
- **No persistence**: Completely ephemeral
- **Lifetime**: Voice feature enable → disable
- **Purpose**: Runtime state only, no historical data

---

## Performance Considerations

### Memory Footprint

| Entity | Count | Size per Instance | Total |
|--------|-------|-------------------|-------|
| VoiceConfiguration | 1 | ~500 bytes | ~500 bytes |
| CharacterProfile | ~5 profiles | ~1-2 KB each | ~10 KB |
| VoiceSession | 1 | ~2 KB | ~2 KB |
| Audio Buffers | Variable | ~100 KB during recording | ~100 KB peak |

**Total estimated memory**: <150 KB (negligible)

### Disk Usage

- Configuration file: <1 KB
- Character profiles: <10 KB total
- No audio recording storage (streaming only)

**Total disk usage**: <15 KB

---

## Security Considerations

### Sensitive Data

1. **OpenAI API Key**: Stored in `voice-config.json`
   - **Protection**: File permissions (chmod 600)
   - **Risk**: If compromised, attacker can use API quota
   - **Mitigation**: Allow environment variable override (`OPENAI_API_KEY`)

2. **Voice Recordings**: Not persisted
   - **Protection**: Audio streams not written to disk
   - **Risk**: None (ephemeral data)

3. **Transcribed Commands**: Not logged
   - **Protection**: Command text not written to files
   - **Risk**: Low (only in memory during processing)

### Data Privacy

- No voice data sent to third parties except OpenAI (for STT/TTS)
- No telemetry or usage tracking
- No cloud storage of configurations or profiles
- User has full control over API key

---

## Migration and Versioning

### Configuration Version

Add `configVersion` field to `VoiceConfiguration`:

```typescript
interface VoiceConfiguration {
  configVersion: 1;
  // ...existing fields
}
```

### Migration Strategy

If schema changes in future:
1. Detect old config version
2. Apply transformation to new schema
3. Write migrated config with new version number
4. Backup old config as `voice-config.json.v{old_version}.backup`

**Current version**: 1 (initial release)

---

## Testing Checklist

### Data Validation Tests

- [ ] VoiceConfiguration validates all fields on load
- [ ] Invalid `selectedCharacter` name falls back to null with warning
- [ ] Invalid `pushToTalkKey` falls back to default
- [ ] Missing or invalid `apiKey` prevents voice features from enabling

### Character Profile Tests

- [ ] Character profiles load successfully from JSON
- [ ] Invalid character profiles rejected with clear error
- [ ] `preserveTechnicalContent` always enforced as true
- [ ] Character switching applies to next response (not mid-response)

### Voice Session Tests

- [ ] Session state transitions follow defined flow
- [ ] Mutual exclusion enforced (listening XOR playing)
- [ ] Interrupt immediately stops playback
- [ ] Pending responses processed in FIFO order
- [ ] Statistics accurately track performance metrics

### Integration Tests

- [ ] End-to-end: push-to-talk → speak → transcribe → execute → respond → play audio
- [ ] Character transformation preserves technical accuracy (SC-004)
- [ ] Audio device failure degrades gracefully with error message
- [ ] Configuration changes apply without requiring restart (where applicable)

---

## Appendix: TypeScript Type Definitions

Complete type definitions are provided in implementation files:
- `src/config/voice-config.ts` - VoiceConfiguration interface
- `src/character/profile.ts` - CharacterProfile interface
- `src/voice/voice-session.ts` - VoiceSession interface

All interfaces exported for use throughout application.
