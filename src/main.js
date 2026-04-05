// Sinapse&IA — Landing Page
// Neural network canvas + scroll interactions

// ─── Neural Canvas ───────────────────────────────────────────────────────────

const canvas = document.getElementById('neural');
const ctx = canvas.getContext('2d');

let W, H, nodes = [], mouse = { x: -9999, y: -9999 };
const NODE_COUNT = 70;
const MAX_DIST = 160;
const MOUSE_RADIUS = 320;   // raio de influência do mouse
const MOUSE_PULL  = 0.018;  // força de atração suave

function resize() {
  W = canvas.width = canvas.offsetWidth;
  H = canvas.height = canvas.offsetHeight;
}

function initNodes() {
  nodes = [];
  for (let i = 0; i < NODE_COUNT; i++) {
    nodes.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 2 + 1.5,
      pulse: Math.random() * Math.PI * 2,
    });
  }
}

function drawFrame() {
  ctx.clearRect(0, 0, W, H);

  // Update positions
  for (const n of nodes) {
    n.x += n.vx;
    n.y += n.vy;
    n.pulse += 0.018;
    if (n.x < 0 || n.x > W) n.vx *= -1;
    if (n.y < 0 || n.y > H) n.vy *= -1;
  }

  // Draw links
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < MAX_DIST) {
        const alpha = (1 - dist / MAX_DIST) * 0.18;
        ctx.beginPath();
        ctx.strokeStyle = `rgba(91,141,239,${alpha})`;
        ctx.lineWidth = 0.8;
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.stroke();
      }
    }
  }

  // Draw mouse connections — linha principal + reflexo mais grosso
  for (const n of nodes) {
    const dx = n.x - mouse.x;
    const dy = n.y - mouse.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < MOUSE_RADIUS) {
      const t = 1 - dist / MOUSE_RADIUS;

      // linha de fundo (glow largo)
      ctx.beginPath();
      ctx.strokeStyle = `rgba(255,193,7,${t * 0.18})`;
      ctx.lineWidth = 6;
      ctx.moveTo(n.x, n.y);
      ctx.lineTo(mouse.x, mouse.y);
      ctx.stroke();

      // linha central nítida
      ctx.beginPath();
      ctx.strokeStyle = `rgba(255,193,7,${t * 0.75})`;
      ctx.lineWidth = 1.5;
      ctx.moveTo(n.x, n.y);
      ctx.lineTo(mouse.x, mouse.y);
      ctx.stroke();
    }
  }

  // Cursor glow ring
  if (mouse.x > 0) {
    const rg = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 80);
    rg.addColorStop(0,   'rgba(255,193,7,0.18)');
    rg.addColorStop(0.4, 'rgba(255,193,7,0.06)');
    rg.addColorStop(1,   'rgba(255,193,7,0)');
    ctx.beginPath();
    ctx.arc(mouse.x, mouse.y, 80, 0, Math.PI * 2);
    ctx.fillStyle = rg;
    ctx.fill();
  }

  // Draw nodes
  for (const n of nodes) {
    const glow = 0.6 + 0.4 * Math.sin(n.pulse);
    const dist  = Math.hypot(n.x - mouse.x, n.y - mouse.y);
    const isNear = dist < MOUSE_RADIUS;
    const proximity = isNear ? Math.max(0, 1 - dist / MOUSE_RADIUS) : 0;

    // nó atraído suavemente em direção ao mouse
    if (isNear) {
      n.x += (mouse.x - n.x) * MOUSE_PULL * proximity;
      n.y += (mouse.y - n.y) * MOUSE_PULL * proximity;
    }

    const radius = n.r * (1 + proximity * 2.5) * glow;
    const color  = isNear
      ? `rgba(255,${Math.floor(193 + proximity * 62)},7,${0.6 + proximity * 0.4})`
      : `rgba(91,141,239,${0.5 + glow * 0.3})`;

    // halo externo nos nós próximos
    if (proximity > 0.3) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, radius * 2.8, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255,193,7,${proximity * 0.12})`;
      ctx.fill();
    }

    ctx.beginPath();
    ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  requestAnimationFrame(drawFrame);
}

window.addEventListener('resize', () => { resize(); });
window.addEventListener('mousemove', (e) => {
  const rect = canvas.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;
});

resize();
initNodes();
drawFrame();

// ─── Scroll Animations ────────────────────────────────────────────────────────

const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  }
}, { threshold: 0.12 });

document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ─── Counter animation ────────────────────────────────────────────────────────

function animateCounter(el, target, duration = 1600) {
  const start = performance.now();
  const update = (now) => {
    const t = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - t, 3);
    el.textContent = Math.floor(ease * target).toLocaleString('pt-BR') + (el.dataset.suffix || '');
    if (t < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

const counterObserver = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      const target = parseInt(entry.target.dataset.count);
      animateCounter(entry.target, target);
      counterObserver.unobserve(entry.target);
    }
  }
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

// ─── Smooth nav ───────────────────────────────────────────────────────────────

document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', (e) => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ─── Nav scroll ──────────────────────────────────────────────────────────────

const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
});
