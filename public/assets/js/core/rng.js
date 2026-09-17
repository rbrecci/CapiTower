// Random com seed, mulberry32 (docs/04-arquitetura.md secao 3).
// Um combate inteiro usa um so gerador, para ser reproduzivel a partir da seed.

export function criarRng(seed) {
  let estado = seed >>> 0;
  return function proximo() {
    estado = (estado + 0x6d2b79f5) | 0;
    let t = Math.imul(estado ^ (estado >>> 15), 1 | estado);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function inteiroAleatorio(rng, limite) {
  return Math.floor(rng() * limite);
}

export function embaralhar(lista, rng) {
  const copia = lista.slice();
  for (let i = copia.length - 1; i > 0; i--) {
    const j = inteiroAleatorio(rng, i + 1);
    const tmp = copia[i];
    copia[i] = copia[j];
    copia[j] = tmp;
  }
  return copia;
}

export function escolher(lista, rng) {
  return lista[inteiroAleatorio(rng, lista.length)];
}

// Deriva uma seed nova e deterministica a partir de uma seed base mais um sal inteiro
// (docs/06-roadmap.md Fase 2). Serve para dar a cada andar da torre o seu proprio gerador
// (ordem da torre, sorteio de evento, combate do andar) sem reusar o mesmo estado de rng
// entre eles e sem tocar em como combat.js ja usa criarRng/embaralhar.
export function derivarSeed(seedBase, sal) {
  let x = (seedBase >>> 0) ^ Math.imul(sal >>> 0, 0x9e3779b1);
  x = Math.imul(x ^ (x >>> 16), 0x45d9f3b);
  x = Math.imul(x ^ (x >>> 16), 0x45d9f3b);
  x = (x ^ (x >>> 16)) >>> 0;
  return x;
}
