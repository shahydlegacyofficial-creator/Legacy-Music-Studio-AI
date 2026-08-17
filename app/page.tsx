"use client";

import { useEffect, useMemo, useState } from "react";

type View = "create" | "presets" | "engine";
type Status = "idle" | "checking" | "ready" | "generating" | "error";
type Duration = 15 | 30 | 60 | 120;
type Hardware = { gpu_name: string; vram_total_mb: number; vram_free_mb: number; max_duration_seconds: number; tier: string; detected: boolean };

const starterLyrics = `[Intro]\n\n[Verse]\nNeon rain on an empty road\nEvery signal carries the load\n\n[Pre-Chorus]\nI hear the future calling my name\n\n[Chorus]\nWe rise, we burn, we come alive\nThrough the static, we survive\n\n[Instrumental]\n\n[Outro]\nThe signal never dies`;
const starterDirection = `Global Metadata: Progressive metal with cinematic electronic textures. 112 BPM, D minor. Dark verses rising into a triumphant final chorus. Modern, wide production.\n\nVocal Details: Powerful male lead with controlled grit, intimate low verses, layered harmonies and gang vocals in the chorus.\n\nArrangement: Drop-tuned guitars, acoustic drums, sub bass and evolving synth pulses. Atmospheric intro; palm-muted verse; orchestral rise; melodic guitar solo; half-time final chorus.`;
const structureTags = ["Intro", "Verse", "Pre-Chorus", "Chorus", "Bridge", "Instrumental", "Solo", "Outro"];
const presets = [
  { category: "rock", name: "Cinematic Metal", code: "LM-01", mood: "DARK · TRIUMPHANT", tempo: "112 BPM", direction: starterDirection },
  { category: "rock", name: "Progressive Djent", code: "LM-02", mood: "TECHNICAL · HEAVY", tempo: "128 BPM", direction: "Global Metadata: Technical progressive djent at 128 BPM in F-sharp minor. Precise, futuristic and aggressive with sudden atmospheric space. Tight contemporary mix.\n\nVocal Details: Rhythmic low-register male vocals, controlled screams in accents, clean soaring hook with stacked harmonies.\n\nArrangement: Eight-string syncopated guitars, punchy drums, angular bass, glitch textures and ambient clean guitars. Complex verse groove, open chorus and polyrhythmic breakdown." },
  { category: "global", name: "Maldivian Ambient", code: "LM-03", mood: "OCEANIC · INTIMATE", tempo: "78 BPM", direction: "Global Metadata: Maldivian ocean ambient at 78 BPM, warm major mode. Intimate, reflective and cinematic, evoking moonlight over the Indian Ocean.\n\nVocal Details: Airy close-mic lead, soft doubles and wordless floating harmonies.\n\nArrangement: Fingerpicked guitar, hand percussion, low frame drum, glassy pads, water textures and restrained bass." },
  { category: "electronic", name: "Retro Signal", code: "LM-04", mood: "NEON · DRIVING", tempo: "105 BPM", direction: "Global Metadata: Dark cinematic synthwave at 105 BPM in C minor. Neon, nocturnal and determined with analog retro-future character.\n\nVocal Details: Cool restrained male lead, intimate verses and an octave-doubled chorus.\n\nArrangement: Pulsing analog bass, gated drums, arpeggiated synths, chorus guitar and atmospheric pads." },
  { category: "cinematic", name: "Legacy Film Score", code: "LM-05", mood: "ORCHESTRAL · EPIC", tempo: "92 BPM", direction: "Global Metadata: Modern cinematic orchestral score at 92 BPM in E minor. Mysterious opening and emotionally victorious finale.\n\nVocal Details: Instrumental with optional distant wordless male choir.\n\nArrangement: Low strings, felt piano, solo electric guitar, brass swells, taiko percussion and hybrid impacts." },
  { category: "rock", name: "Six String Horizon", code: "LM-06", mood: "MELODIC · EXPANSIVE", tempo: "96 BPM", direction: "Global Metadata: Instrumental melodic progressive rock at 96 BPM in A minor. Soulful, expansive and technically refined.\n\nVocal Details: Instrumental; lead guitar carries the vocal-like melody.\n\nArrangement: Expressive electric lead, clean arpeggios, warm bass, live drums and subtle ambient synths." },
  { category: "pop", name: "Modern Pop Anthem", code: "LM-07", mood: "BRIGHT · EMOTIONAL", tempo: "118 BPM", direction: "Global Metadata: Modern radio pop at 118 BPM in B major. Bright, emotional and instantly memorable with glossy premium production.\n\nVocal Details: Confident contemporary lead, intimate verse delivery, stacked doubles and wide harmonies.\n\nArrangement: Punchy drums, warm synth bass, muted guitar, piano accents and shimmering pads; explosive singalong chorus." },
  { category: "rock", name: "Modern Arena Rock", code: "LM-08", mood: "BOLD · ANTHEMIC", tempo: "126 BPM", direction: "Global Metadata: Modern arena rock at 126 BPM in E minor. Bold, energetic and triumphant with a huge live-band character.\n\nVocal Details: Powerful raspy lead, direct verses, octave doubles and crowd-ready harmonies.\n\nArrangement: Crunchy guitars, melodic lead lines, live drums, driving bass, massive chorus and concise guitar solo." },
  { category: "pop", name: "K-Pop Neon Rush", code: "LM-09", mood: "FUTURE · ADDICTIVE", tempo: "124 BPM", direction: "Global Metadata: High-energy K-pop at 124 BPM in F-sharp minor. Futuristic, playful and addictive with rapid contrasts.\n\nVocal Details: Mixed group vocals, airy pre-chorus, confident rap break, layered ad-libs and bright hook.\n\nArrangement: Punchy electronic drums, elastic bass, glossy synths, filtered guitar, dance break and maximal final chorus." },
  { category: "rnb", name: "Velvet R&B", code: "LM-10", mood: "LATE NIGHT · SOULFUL", tempo: "74 BPM", direction: "Global Metadata: Contemporary R&B at 74 BPM in C-sharp minor. Intimate, sensual and nocturnal with warm high-end production.\n\nVocal Details: Smooth expressive lead, breathy verses, agile runs, falsetto and lush harmony stacks.\n\nArrangement: Rhodes, sub bass, sparse rim-shot drums, muted guitar and atmospheric synth layers." },
  { category: "electronic", name: "Lo-Fi Study Tape", code: "LM-11", mood: "CALM · NOSTALGIC", tempo: "72 BPM", direction: "Global Metadata: Instrumental lo-fi hip-hop at 72 BPM in D major. Calm, nostalgic and focused with soft tape saturation.\n\nVocal Details: Instrumental; optional distant chopped vocal texture as ambience.\n\nArrangement: Dusty drums, warm Rhodes, mellow jazz guitar, rounded bass and vinyl texture with seamless loop structure." },
  { category: "electronic", name: "Festival EDM", code: "LM-12", mood: "EUPHORIC · MASSIVE", tempo: "128 BPM", direction: "Global Metadata: Melodic festival EDM at 128 BPM in A major. Euphoric, high-impact and emotional with a wide club master.\n\nVocal Details: Airy pop lead, short emotional verse and layered vocoder hook.\n\nArrangement: Four-on-the-floor kick, sidechained supersaws, plucks, sub bass, cinematic risers and huge melodic drops." },
  { category: "global", name: "Afrobeats Sunset", code: "LM-13", mood: "WARM · INFECTIOUS", tempo: "104 BPM", direction: "Global Metadata: Contemporary Afrobeats at 104 BPM in G major. Warm, romantic and infectious with a relaxed coastal atmosphere.\n\nVocal Details: Melodic rhythmic lead, conversational verses and call-and-response hook.\n\nArrangement: Syncopated percussion, log drum accents, highlife guitar, rounded bass, soft keys and airy pads." },
  { category: "hiphop", name: "Cinematic Trap", code: "LM-14", mood: "DARK · COMMANDING", tempo: "142 BPM", direction: "Global Metadata: Dark cinematic trap at 142 BPM in F minor. Commanding, tense and luxurious with hard low end.\n\nVocal Details: Focused rhythmic rap, melodic phrases, whispered doubles and chant-like hook.\n\nArrangement: Deep 808 slides, sharp hats, punchy kick, ominous piano, distorted brass and reverse textures." },
  { category: "acoustic", name: "Acoustic Ballad", code: "LM-15", mood: "HONEST · CINEMATIC", tempo: "68 BPM", direction: "Global Metadata: Intimate acoustic pop ballad at 68 BPM in G major. Honest, vulnerable and gradually cinematic.\n\nVocal Details: Close emotional lead, restrained harmony and full layered final chorus.\n\nArrangement: Fingerpicked acoustic guitar, felt piano, soft bass, brushed drums and late-arriving strings." },
  { category: "rock", name: "Indie Alternative", code: "LM-16", mood: "RAW · DREAMY", tempo: "108 BPM", direction: "Global Metadata: Indie alternative rock at 108 BPM in D major. Raw, dreamy and bittersweet with analog character.\n\nVocal Details: Understated lead, conversational verses, imperfect doubles and group harmonies.\n\nArrangement: Chorus guitars, live drums, melodic bass, upright piano and hazy synth bed." },
  { category: "global", name: "Island Reggae", code: "LM-17", mood: "SUNLIT · EASY", tempo: "86 BPM", direction: "Global Metadata: Modern island reggae at 86 BPM in A major. Sunlit, easygoing and hopeful with warm organic production.\n\nVocal Details: Relaxed melodic lead, friendly response vocals and rich chorus harmony.\n\nArrangement: Offbeat clean guitar, one-drop drums, melodic bass, organ bubble and light hand percussion." },
  { category: "rnb", name: "Jazz Soul Lounge", code: "LM-18", mood: "SMOOTH · TIMELESS", tempo: "82 BPM", direction: "Global Metadata: Neo-soul jazz lounge at 82 BPM in E-flat major. Smooth, sophisticated and timeless.\n\nVocal Details: Rich soulful lead, behind-the-beat phrasing and gospel-inspired harmonies.\n\nArrangement: Rhodes, upright-style bass, brushed drums, jazz guitar and muted trumpet accents." },
  { category: "rnb", name: "Future Funk", code: "LM-19", mood: "GROOVY · ELECTRIC", tempo: "116 BPM", direction: "Global Metadata: Modern future funk at 116 BPM in C minor. Groovy, electric and celebratory with tight retro-modern production.\n\nVocal Details: Charismatic lead, falsetto accents, gang responses and vocoder hook.\n\nArrangement: Slap bass, clipped rhythm guitar, dry drums, analog brass and talkbox synth." },
  { category: "electronic", name: "Dark Melodic Techno", code: "LM-20", mood: "HYPNOTIC · CINEMATIC", tempo: "126 BPM", direction: "Global Metadata: Dark melodic techno at 126 BPM in D minor. Hypnotic, cinematic and steadily escalating.\n\nVocal Details: Mostly instrumental; sparse processed spoken phrase as rhythmic motif.\n\nArrangement: Driving kick, rolling bass, evolving analog sequence, metallic percussion and wide atmospheric chords." },
];

export default function Home() {
  const [view, setView] = useState<View>("create");
  const [lyrics, setLyrics] = useState(starterLyrics);
  const [direction, setDirection] = useState(starterDirection);
  const [duration, setDuration] = useState<Duration>(15);
  const [seed, setSeed] = useState(7);
  const [endpoint, setEndpoint] = useState("http://127.0.0.1:8787");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("Desktop runtime not linked");
  const [audio, setAudio] = useState<string | null>(null);
  const [clock, setClock] = useState("");
  const [hardware, setHardware] = useState<Hardware>({ gpu_name: "NVIDIA GPU", vram_total_mb: 0, vram_free_mb: 0, max_duration_seconds: 30, tier: "LOW VRAM SAFE", detected: false });
  const [presetFilter, setPresetFilter] = useState("all");
  const [presetSearch, setPresetSearch] = useState("");
  const frames = useMemo(() => duration * 25, [duration]);
  const visiblePresets = useMemo(() => presets.filter(preset => (presetFilter === "all" || preset.category === presetFilter) && `${preset.name} ${preset.mood} ${preset.tempo} ${preset.category}`.toLowerCase().includes(presetSearch.toLowerCase())), [presetFilter, presetSearch]);

  useEffect(() => {
    const tick = () => setClock(new Date().toLocaleTimeString([], { hour12: false }));
    tick(); const timer = window.setInterval(tick, 1000); return () => window.clearInterval(timer);
  }, []);

  async function checkEngine() {
    setStatus("checking"); setMessage("Checking desktop runtime…");
    try {
      const response = await fetch(`${endpoint.replace(/\/$/, "")}/api/status`);
      if (!response.ok) throw new Error();
      const data = await response.json();
      setStatus(data.state === "ready" ? "ready" : "idle");
      setMessage(data.detail || "Desktop runtime linked");
      const hardwareResponse = await fetch(`${endpoint.replace(/\/$/, "")}/api/hardware`);
      if (hardwareResponse.ok) setHardware(await hardwareResponse.json());
    } catch {
      setStatus("error");
      setMessage("Open the Windows desktop studio to generate locally");
    }
  }

  async function generate() {
    setStatus("generating"); setMessage("MiniMax core is composing…");
    if (audio) URL.revokeObjectURL(audio);
    setAudio(null);
    try {
      const response = await fetch(`${endpoint.replace(/\/$/, "")}/v1/audio/speech`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: "MiniMaxAI/MiniMax-Music3", input: lyrics, instructions: direction, response_format: "flac", seed, max_new_tokens: frames, stream: false })
      });
      if (!response.ok) throw new Error(await response.text());
      setAudio(URL.createObjectURL(await response.blob())); setStatus("ready"); setMessage("Track complete · stored locally");
    } catch {
      setStatus("error"); setMessage("Desktop runtime unavailable — use the included Windows dashboard");
    }
  }

  function loadPreset(index: number) { setDirection(presets[index].direction); setView("create"); }

  return <main className="legacy-shell">
    <div className="stars" />
    <header className="topbar">
      <div className="brand"><i /><b>LEGACY</b><span>MUSIC STUDIO</span><em /> <small>CORE · LOCAL</small></div>
      <div className="statusline"><span>MALÉ {clock}</span><b className={status === "ready" ? "online" : status === "error" ? "fault" : ""}><i />{status === "ready" ? "LINK · ONLINE" : "DESKTOP LINK"}</b></div>
    </header>

    <aside className="leftRail">
      <nav>
        {(["create", "presets", "engine"] as View[]).map((item, index) => <button key={item} className={view === item ? "active" : ""} onClick={() => setView(item)}><span>0{index + 1}</span><b>{item.toUpperCase()}</b><small>{item === "create" ? "NEW CUE" : item === "presets" ? "SOUND SYSTEMS" : "RUNTIME STATUS"}</small></button>)}
      </nav>
      <section className="modelCard"><p>ACTIVE MODEL</p><div><span>M3</span><b>MiniMax Music 3<small>INT8 · LOW VRAM</small></b></div><dl><dt>COMPUTE</dt><dd>CUDA</dd><dt>OUTPUT</dt><dd>32 KHZ FLAC</dd><dt>PROFILE</dt><dd>8 GB SAFE</dd></dl></section>
      <a href="https://www.shahydlegacy.com" target="_blank" rel="noreferrer">SHAHYDLEGACY.COM ↗</a>
    </aside>

    <section className="workspace">
      {view === "create" && <>
        <div className="hero"><div><p>LOCAL MUSIC GENERATION // WEB COMPANION</p><h1>Compose at the<br/><em>edge of the signal.</em></h1></div><div className="core"><i/><i/><span>LEGACY<br/>CORE</span></div></div>
        <div className="createGrid">
          <div className="editors">
            <article className="panel"><Title number="01" name="LYRICS + STRUCTURE" meta={`${lyrics.length} CHARACTERS`} /><textarea className="lyrics" value={lyrics} onChange={e => setLyrics(e.target.value)} /><div className="tags">{structureTags.map(tag => <button key={tag} onClick={() => setLyrics(value => `${value.trimEnd()}\n\n[${tag}]\n`)}>+ {tag.toUpperCase()}</button>)}</div></article>
            <article className="panel"><Title number="02" name="MUSIC DIRECTION" meta="STRUCTURED CAPTION" /><textarea className="direction" value={direction} onChange={e => setDirection(e.target.value)} /><div className="guides"><span>G · GENRE / BPM / KEY</span><span>V · VOICE / TIMBRE</span><span>A · ARRANGEMENT / MIX</span></div></article>
          </div>
          <aside className="controls">
            <article className="panel"><Title number="03" name="GENERATION CONTROL" meta={hardware.detected ? `${Math.round(hardware.vram_total_mb / 1024)} GB PROFILE` : "8 GB SAFE"} /><label>TARGET LENGTH <small>HARDWARE-AWARE</small></label><div className="duration">{([15, 30, 60, 120] as const).map(value => <button key={value} className={duration === value ? "active" : ""} disabled={value > hardware.max_duration_seconds} onClick={() => setDuration(value)}><strong>{value < 60 ? `00:${value}` : `${String(value / 60).padStart(2, "0")}:00`}</strong><small>{value === 15 ? "SAFE START" : value === 30 ? "8 GB MAX" : value === 60 ? (hardware.max_duration_seconds >= 60 ? "16 GB+ · UNLOCKED" : "16 GB+ · LOCKED") : (hardware.max_duration_seconds >= 120 ? "24 GB+ · UNLOCKED" : "24 GB+ · LOCKED")}</small></button>)}</div><div className="pressure"><i style={{width: duration === 15 ? "25%" : duration === 30 ? "45%" : duration === 60 ? "70%" : "100%"}} /></div><hr/><label>SEED <small>REPEATABLE</small></label><div className="seed"><input type="number" value={seed} onChange={e => setSeed(+e.target.value)} /><button onClick={() => setSeed(Math.floor(Math.random() * 100000))}>↻</button></div><div className="specs"><span><small>FRAMES</small>{frames}</span><span><small>FORMAT</small>FLAC</span><span><small>RATE</small>32 KHZ</span></div><button className="generate" disabled={status === "generating"} onClick={generate}>✦ {status === "generating" ? "GENERATING…" : "GENERATE TRACK"}</button><p className="note">Your 8 GB profile stays protected at 30 seconds. 60 seconds and 2 minutes unlock only when the desktop reports enough VRAM.</p></article>
            <article className="panel output"><Title number="04" name="ACTIVE OUTPUT" meta={status.toUpperCase()} />{audio ? <><div className="wave">{Array.from({length: 44}, (_, i) => <i key={i} style={{height: `${12 + (i * 23 + seed) % 75}%`}} />)}</div><audio controls src={audio}/><a href={audio} download={`legacy-music-${seed}.flac`}>DOWNLOAD LOSSLESS FLAC ↓</a></> : <div className="empty"><i><b/></i><strong>{status === "generating" ? "MINIMAX CORE IS COMPOSING" : "AWAITING GENERATION"}</strong><p>{message}</p></div>}</article>
          </aside>
        </div>
      </>}

      {view === "presets" && <><SectionHead eyebrow="DIRECTION SYSTEMS // QUICK START" title="Genre systems." copy="Twenty curated starting points shaped for MiniMax Music 3’s structured caption format." /><div className="presetToolbar"><label><span>⌕</span><input value={presetSearch} onChange={event => setPresetSearch(event.target.value)} placeholder="SEARCH GENRES, MOODS OR TEMPO" /></label><div>{["all", "pop", "rock", "rnb", "electronic", "cinematic", "global", "hiphop", "acoustic"].map(category => <button key={category} className={presetFilter === category ? "active" : ""} onClick={() => setPresetFilter(category)}>{category === "rnb" ? "R&B" : category === "hiphop" ? "HIP-HOP" : category.toUpperCase()}</button>)}</div><small>{visiblePresets.length} SYSTEMS</small></div><div className="presetGrid">{visiblePresets.map(preset => { const index = presets.indexOf(preset); return <button key={preset.code} onClick={() => loadPreset(index)}><span>{`${preset.code} // ${preset.category.toUpperCase()} · ${preset.mood}`}</span><h2>{preset.name}</h2><p>{preset.direction.split("\n")[0].replace("Global Metadata: ", "")}</p><footer><small>{preset.tempo}</small><b>LOAD SYSTEM →</b></footer></button>; })}</div></>}

      {view === "engine" && <><SectionHead eyebrow="SYSTEM CORE // DESKTOP RUNTIME" title="Engine link." copy="The MiniMax Music 3 engine runs privately on your Windows PC. This page checks the same local endpoint used by the desktop studio." /><div className="engineGrid"><article className="panel engineHero"><div className="engineOrb">M3</div><div><p>CURRENT STATE</p><h2>{status === "ready" ? "LINK ONLINE" : status === "checking" ? "CHECKING CORE" : "DESKTOP REQUIRED"}</h2><span>{message}</span></div></article><article className="panel engineForm"><Title number="01" name="LOCAL ENDPOINT" /><label>DESKTOP RUNTIME URL</label><input value={endpoint} onChange={e => setEndpoint(e.target.value)} /><button className="generate" onClick={checkEngine}>↻ CHECK ENGINE</button></article><article className="panel protocol"><Title number="02" name="HARDWARE PROFILE" /><ul><li>{hardware.detected ? hardware.gpu_name : "Connect the desktop to detect the NVIDIA GPU."}</li><li>{hardware.detected ? `${Math.round(hardware.vram_total_mb / 1024)} GB VRAM · ${hardware.tier}` : "8 GB defaults to the protected 15–30 second range."}</li><li>60 seconds requires at least 16 GB VRAM.</li><li>2 minutes requires at least 24 GB VRAM.</li></ul></article></div></>}
    </section>

    <aside className="rightRail"><section><p>SESSION STATUS</p><dl><dt>CORE</dt><dd>{status === "ready" ? "ONLINE" : "STANDBY"}</dd><dt>MODE</dt><dd>LOCAL / PRIVATE</dd><dt>DURATION</dt><dd>{duration < 60 ? `00:${duration}` : `${String(duration / 60).padStart(2, "0")}:00`} {duration <= 30 ? "SAFE" : "EXTENDED"}</dd><dt>DRAFT</dt><dd>IN SESSION</dd></dl></section><section className="quote"><b>“</b><p>SIX STRINGS OUT OF THE INDIAN OCEAN — NOW WIRED INTO A LOCAL MUSIC CORE.</p><small>LEGACY STUDIO · MALÉ</small></section></aside>
  </main>;
}

function Title({ number, name, meta }: { number: string; name: string; meta?: string }) { return <div className="panelTitle"><div><span>{number}</span><h2>{name}</h2></div>{meta && <small>{meta}</small>}</div>; }
function SectionHead({ eyebrow, title, copy }: { eyebrow: string; title: string; copy: string }) { return <div className="sectionHead"><p>{eyebrow}</p><h1>{title}</h1><span>{copy}</span></div>; }
