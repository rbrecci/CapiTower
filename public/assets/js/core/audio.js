// Fase 7: som sem nenhum arquivo de audio (nao ha asset de som no projeto e baixar de fonte
// externa nao e algo que da pra fazer sozinho aqui, docs/09). Efeitos curtos sintetizados na
// hora com a Web Audio API (osciladores com envelope de ganho), tocados por combatView.js,
// cardView.js e towerView.js. Um AudioContext so, criado sob demanda no primeiro som (autoplay
// policy dos navegadores bloqueia criar/tocar audio antes de um gesto do usuario), e um mudo
// persistido em localStorage.

const CHAVE_MUDO = "capitower_som_mudo";
let ctx = null;

function contexto() {
  if (!ctx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
  }
  if (ctx.state === "suspended") ctx.resume();
  return ctx;
}

export function estaMudo() {
  try {
    return localStorage.getItem(CHAVE_MUDO) === "1";
  } catch {
    return false;
  }
}

export function alternarMudo() {
  const mudo = !estaMudo();
  try {
    localStorage.setItem(CHAVE_MUDO, mudo ? "1" : "0");
  } catch {
    // localStorage indisponivel (aba privada, etc.): so nao persiste, o jogo continua normal.
  }
  return mudo;
}

function tocarTom({ freq, duracao = 0.12, tipo = "sine", volume = 0.18, deslizeFreq = null }) {
  if (estaMudo()) return;
  const audio = contexto();
  if (!audio) return;
  const osc = audio.createOscillator();
  const ganho = audio.createGain();
  osc.type = tipo;
  osc.frequency.setValueAtTime(freq, audio.currentTime);
  if (deslizeFreq) {
    osc.frequency.exponentialRampToValueAtTime(deslizeFreq, audio.currentTime + duracao);
  }
  ganho.gain.setValueAtTime(volume, audio.currentTime);
  ganho.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + duracao);
  osc.connect(ganho).connect(audio.destination);
  osc.start();
  osc.stop(audio.currentTime + duracao + 0.02);
}

export function somCarta() {
  tocarTom({ freq: 520, duracao: 0.1, tipo: "triangle", volume: 0.14 });
}

export function somDano() {
  tocarTom({ freq: 180, duracao: 0.16, tipo: "sawtooth", volume: 0.2, deslizeFreq: 70 });
}

export function somCura() {
  tocarTom({ freq: 660, duracao: 0.18, tipo: "sine", volume: 0.16, deslizeFreq: 880 });
}

export function somBloco() {
  tocarTom({ freq: 300, duracao: 0.12, tipo: "square", volume: 0.12 });
}

export function somInvocacao() {
  tocarTom({ freq: 420, duracao: 0.22, tipo: "triangle", volume: 0.15, deslizeFreq: 620 });
}

export function somMorteInimigo() {
  tocarTom({ freq: 240, duracao: 0.3, tipo: "sawtooth", volume: 0.18, deslizeFreq: 60 });
}

export function somClique() {
  tocarTom({ freq: 440, duracao: 0.05, tipo: "square", volume: 0.08 });
}

export function somVitoria() {
  [523, 659, 784].forEach((freq, i) => {
    setTimeout(() => tocarTom({ freq, duracao: 0.22, tipo: "triangle", volume: 0.16 }), i * 110);
  });
}

export function somDerrota() {
  [330, 262, 196].forEach((freq, i) => {
    setTimeout(() => tocarTom({ freq, duracao: 0.28, tipo: "sawtooth", volume: 0.16 }), i * 140);
  });
}
