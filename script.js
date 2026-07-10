// Latest tweet link. Update this after posting a new archive tweet.
const LATEST_TWEET_URL = "https://x.com/NoRefundsArc/status/2073718849191505962?s=20";

// Google Apps Script endpoint for collecting whitelist submissions.
// Replace this URL after deploying your Google Apps Script.
const SHEET_API_URL = "https://script.google.com/macros/s/AKfycbxUHajYs7yxsGKOiXkW-QYfRGJT8EJ-d3ab3mMX5G3TgQrsP06MTYZ-MXR2FYFtEtvY/exec";

const machine = document.querySelector(".machine-experience");
const startButton = document.querySelector("#startMachine");
const machineScreen = document.querySelector("#machineScreen");
const heroStart = document.querySelector("#heroStart");
const audioToggle = document.querySelector("#audioToggle");
const backgroundMusic = document.querySelector("#backgroundMusic");

const crtModal = document.getElementById("crtModal");
const receiptOverlay = document.getElementById("receiptOverlay");
const bootText = document.getElementById("bootText");
const crtForm = document.getElementById("crtForm");
const closeCrtBtn = document.getElementById("closeCrtBtn");
const closeReceiptBtn = document.getElementById("closeReceiptBtn");
const shareReceiptBtn = document.getElementById("shareReceiptBtn");
const latestTweetLink = document.getElementById("latestTweetLink");

if (latestTweetLink) {
  latestTweetLink.href = LATEST_TWEET_URL;
}

let audioContext;
let staticNodes;

document.querySelectorAll(".receipt-card img").forEach((image) => {
  function markFailed() { image.closest(".receipt-card")?.classList.add("image-failed"); }
  image.addEventListener("error", markFailed);
  if (image.complete && image.naturalWidth === 0) { markFailed(); }
});

function setAudioButton(on) {
  audioToggle.innerHTML = `<span class="audio-dot" aria-hidden="true"></span>Audio ${on ? "On" : "Off"}`;
  audioToggle.setAttribute("aria-pressed", on ? "true" : "false");
}
function setAudioButtonLoading() {
  audioToggle.innerHTML = '<span class="audio-dot" aria-hidden="true"></span>Audio...';
  audioToggle.setAttribute("aria-pressed", "false");
}
function getAudioContext() {
  audioContext ||= new (window.AudioContext || window.webkitAudioContext)();
  return audioContext;
}
function tone(frequency, duration, type = "square", gain = 0.035, delay = 0) {
  const context = getAudioContext();
  const oscillator = context.createOscillator();
  const volume = context.createGain();
  const start = context.currentTime + delay;
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, start);
  volume.gain.setValueAtTime(0.0001, start);
  volume.gain.exponentialRampToValueAtTime(gain, start + 0.012);
  volume.gain.exponentialRampToValueAtTime(0.0001, start + duration);
  oscillator.connect(volume);
  volume.connect(context.destination);
  oscillator.start(start);
  oscillator.stop(start + duration + 0.03);
}
function startStaticAudio() {
  if (staticNodes) return;
  const context = getAudioContext();
  const buffer = context.createBuffer(1, context.sampleRate * 2, context.sampleRate);
  const data = buffer.getChannelData(0);
  const staticSource = context.createBufferSource();
  const filter = context.createBiquadFilter();
  const noiseGain = context.createGain();
  for (let index = 0; index < data.length; index += 1) { data[index] = Math.random() * 2 - 1; }
  staticSource.buffer = buffer;
  staticSource.loop = true;
  filter.type = "lowpass";
  filter.frequency.value = 1800;
  noiseGain.gain.value = 0.052;
  staticSource.connect(filter);
  filter.connect(noiseGain);
  noiseGain.connect(context.destination);
  staticSource.start();
  staticNodes = { staticSource, noiseGain };
}
function startMusicAudio() {
  if (!backgroundMusic || !backgroundMusic.paused) return;
  backgroundMusic.volume = 0.72;
  setAudioButtonLoading();
  backgroundMusic.play().then(() => setAudioButton(true)).catch(() => setAudioButton(false));
}
function stopMusicAudio() {
  if (!backgroundMusic || backgroundMusic.paused) return;
  backgroundMusic.pause();
  setAudioButton(false);
}
function toggleMusicAudio() {
  if (!backgroundMusic) return;
  if (!backgroundMusic.paused) { stopMusicAudio(); } else { startMusicAudio(); }
}
function playSound(name) {
  try {
    if (name === "play") { tone(196, 0.12, "sine", 0.052); tone(293.66, 0.16, "triangle", 0.05, 0.11); tone(392, 0.22, "sine", 0.046, 0.25); }
    if (name === "tick") { tone(659.25, 0.06, "sine", 0.04); }
    if (name === "success") { tone(392, 0.12, "sine", 0.052); tone(523.25, 0.16, "triangle", 0.05, 0.12); tone(659.25, 0.22, "sine", 0.046, 0.28); }
  } catch {}
}

function startTape() {
  startStaticAudio();
  playSound("play");
  machine.dataset.machineState = "active";
  machineScreen.innerHTML = '<div class="screen-static"></div><span>WL TAPE LOADED</span><strong>COMPLETE RECEIPT</strong>';
  startButton.textContent = "Playing";
  
  setTimeout(() => {
    crtModal.classList.remove('crt-modal-hidden');
    setTimeout(() => crtModal.classList.add('active'), 50);
    typeWriter("SYSTEM ONLINE...\nLOADING ARCHIVE PROTOCOL...\n", bootText, 40, () => {
      setTimeout(() => crtForm.classList.remove('crt-form-hidden'), 500);
    });
  }, 800);
}

function typeWriter(text, element, speed, callback) {
  let i = 0; element.innerHTML = "";
  function type() {
    if (i < text.length) { element.innerHTML += text.charAt(i); i++; setTimeout(type, speed); }
    else if (callback) callback();
  }
  type();
}

function normalizeTwitter(value) {
  const clean = value.trim().replace(/^@+/, "");
  return `@${clean}`;
}
function makeApplicationId(wallet) {
  const tail = wallet.slice(-4).toUpperCase();
  const stamp = Date.now().toString(36).toUpperCase().slice(-5);
  return `NRA-${tail}-${stamp}`;
}
function getApplications() {
  try { return JSON.parse(localStorage.getItem("nraWhitelist") || "[]"); } catch { return []; }
}
function saveApplications(applications) {
  try { localStorage.setItem("nraWhitelist", JSON.stringify(applications)); } catch {}
}

// Send submission to Google Sheets via Apps Script
async function submitToSheet(application) {
  if (!SHEET_API_URL || SHEET_API_URL.includes("YOUR_GOOGLE_APPS_SCRIPT")) {
    console.warn("Sheet API not configured. Data saved to localStorage only.");
    return false;
  }
  try {
    const response = await fetch(SHEET_API_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(application),
    });
    return true;
  } catch (err) {
    console.error("Sheet submission failed:", err);
    return false;
  }
}

heroStart.addEventListener("click", () => {
  document.querySelector("#tapeMachine").scrollIntoView({ behavior: "smooth", block: "center" });
  startTape();
});
audioToggle.addEventListener("click", toggleMusicAudio);
startButton.addEventListener("click", () => { startTape(); });

// 鍏抽棴 CRT 寮圭獥
closeCrtBtn.addEventListener('click', () => {
  crtModal.classList.remove('active');
  setTimeout(() => {
    crtModal.classList.add('crt-modal-hidden');
    bootText.innerHTML = "";
    crtForm.reset();
    crtForm.classList.add('crt-form-hidden');
    document.querySelectorAll('.crt-confirm').forEach(btn => {
      btn.classList.remove('crt-hidden');
      btn.innerHTML = '[ CONFIRM ]';
      btn.style.pointerEvents = 'auto';
      btn.nextElementSibling.classList.add('crt-hidden');
    });
  }, 300);
});

document.querySelectorAll('.crt-confirm').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const targetBtn = e.currentTarget;
    const statusOk = targetBtn.nextElementSibling;
    targetBtn.innerHTML = '[ ... ]';
    targetBtn.style.pointerEvents = 'none';
    setTimeout(() => {
      targetBtn.classList.add('crt-hidden');
      statusOk.classList.remove('crt-hidden');
    }, 800);
  });
});

crtForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const wallet = document.getElementById('crtWallet').value.trim();
  const username = document.getElementById('crtUsername').value.trim();
  
  const step1Ok = document.querySelector('[data-step="1"]').nextElementSibling.classList.contains('glow-text');
  const step2Ok = document.querySelector('[data-step="2"]').nextElementSibling.classList.contains('glow-text');

  if (!step1Ok || !step2Ok) { bootText.innerHTML += "\n> ERROR: PROTOCOL INCOMPLETE."; return; }
  if (!/^0x[a-fA-F0-9]{40}$/.test(wallet)) { bootText.innerHTML += "\n> ERROR: INVALID WALLET_ADDR."; return; }
  if (!username.startsWith('@')) { bootText.innerHTML += "\n> ERROR: OPERATOR_ID MUST START WITH @."; return; }

  const applications = getApplications();
  const alreadyApplied = applications.some((entry) => entry.wallet.toLowerCase() === wallet.toLowerCase());
  if (alreadyApplied) { bootText.innerHTML += "\n> ERROR: WALLET ALREADY REGISTERED."; return; }

  crtForm.classList.add('crt-form-hidden');
  bootText.innerHTML = "> PRINTING SLIP...\n> 鈻堚枅鈻堚枅鈻堚枅鈻堚枅鈻堚枅鈻堚枅鈻堚枅鈻堚枅鈻?100%\n";
  
  setTimeout(() => {
    const receiptId = '#' + Math.floor(10000 + Math.random() * 90000);
    const dateStr = new Date().toISOString().split('T')[0];
    
    document.getElementById('rId').innerText = receiptId;
    document.getElementById('rWallet').innerText = wallet;
    document.getElementById('rOp').innerText = username;
    document.getElementById('rDate').innerText = dateStr;
    
    const application = { id: makeApplicationId(wallet), wallet, twitter: normalizeTwitter(username), followed: true, retweeted: true, followCheck: "self-confirmed", createdAt: new Date().toISOString() };
    applications.push(application);
    saveApplications(applications);
    submitToSheet(application);
    playSound("success");
    
    crtModal.classList.remove('active');
    setTimeout(() => {
      crtModal.classList.add('crt-modal-hidden');
      receiptOverlay.classList.remove('receipt-overlay-hidden');
      setTimeout(() => receiptOverlay.classList.add('active'), 50);
    }, 300);
  }, 2000);
});

closeReceiptBtn.addEventListener('click', () => {
  receiptOverlay.classList.remove('active');
  setTimeout(() => {
    receiptOverlay.classList.add('receipt-overlay-hidden');
    machine.dataset.machineState = "idle";
    machineScreen.innerHTML = '<div class="screen-static"></div><span class="standby-copy">NO SIGNAL</span>';
    startButton.textContent = "Play";
  }, 500);
});

// Random memory copy for sharing receipts.
const memoryQuotes = [
  "Found an old ticket stub in a coat pocket. The cinema is gone, but for a second, I was back in that seat. @NoRefundsArc",
  "Some places disappear, but the smell of their coffee stays in your memory forever. @NoRefundsArc",
  "Paid in cash. No record left, except this faded slip. Proof I was there. @NoRefundsArc",
  "The diner closed ten years ago. I still dream about the pie they served at 2 AM. @NoRefundsArc",
  "A receipt is just paper, until you realize it's the last thing you bought together. @NoRefundsArc",
  "They renamed the road. The gas station is a parking lot now. But I remember the pump. @NoRefundsArc",
  "No refunds. Just memories. And a piece of thermal paper that refuses to fade. @NoRefundsArc",
  "I kept the receipt not for the return policy, but for the date written on the back. @NoRefundsArc",
  "The video store is gone. The late fee was worth it. @NoRefundsArc",
  "We paid for the room in cash. The motel is demolished now. Only this slip remains. @NoRefundsArc",
  "Some purchases aren't about the item. They're about the moment you couldn't let go. @NoRefundsArc",
  "The archivist doesn't collect things. He collects the silence after the store closes. @NoRefundsArc"
];

shareReceiptBtn.addEventListener('click', () => {
  const receiptId = document.getElementById('rId').innerText;
  const randomMemory = memoryQuotes[Math.floor(Math.random() * memoryQuotes.length)];
  const tweetText = `${randomMemory}\n\nRECEIPT ID: ${receiptId}\n\n#NoRefundsArchive`;
  window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`, '_blank');
});

// Counter files: show mint/process/FAQ as in-page archive cards.
const counterFiles = {
  notes: {
    kicker: "",
    title: "Recovered Notes",
    intro: "Four pages were pulled from the drawer first. They do not explain the whole archive. They only keep the beginning.",
    cards: [
      { label: "", title: "The Archive Is Not a Store", body: "A collection of fictional receipts from places that no longer exist. Not a roadmap. Not a mascot. Just small proofs left on fading paper." },
      { label: "", title: "Why the Archive Exists", body: "The store is gone. The proof stayed. Somewhere, a scanner kept working long after the counter closed." },
      { label: "", title: "What Survives", body: "Date. Time. Item. Total. Paid cash. Faces fade first. The receipt keeps only the facts." },
      { label: "", title: "What the Archive Keeps", body: "Evidence too small for history, but too personal to throw away. Old receipts. Closed stores. No refunds." }
    ]
  },
  mint: {
    kicker: "",
    title: "Mint Information",
    intro: "The register keeps only the numbers that matter. Supply, claims, price, and the moment the sealed slips open.",
    cards: [
      { label: "", title: "3333 Receipts", body: "A fixed drawer of archived slips from places that no longer exist." },
      { label: "", title: "1111 Free Claims", body: "Early collectors may print one whitelist slip. One wallet, one claim." },
      { label: "", title: "0.0006 ETH", body: "After the first drawer closes, the remaining receipts move to the public counter." },
      { label: "", title: "Reveal After Mint", body: "The sealed slips open with store, stamp, damage, handwriting, and surrounding evidence." }
    ]
  },
  process: {
    kicker: "",
    title: "Archive Process",
    intro: "The archive does not move like a loud roadmap. It opens one drawer, then another.",
    cards: [
      { label: "", title: "Intake", body: "Receipts are recovered, scanned, numbered, and placed by the store they came from." },
      { label: "", title: "Whitelist Tape", body: "The first collectors follow the archive signal and print one claim from the terminal." },
      { label: "", title: "Public Counter", body: "The remaining receipts are left on the counter until the drawer is empty." },
      { label: "", title: "Reveal", body: "Each slip shows its found format, paper damage, stamp, handwriting, and quiet evidence." },
      { label: "", title: "After Hours", body: "More archive logs, recovered stories, collector files, and printable-style records may surface later." }
    ]
  },
  faq: {
    kicker: "",
    title: "FAQ",
    intro: "A few questions were written on the back of the counter tag. The answers stayed short.",
    cards: [
      { label: "", title: "Is this a PFP?", body: "No. The receipt is the character. The paper is the proof." },
      { label: "", title: "Are the stores real?", body: "No. All store names, items, locations, and stories are fictional." },
      { label: "", title: "Why receipts?", body: "A receipt is cheap paper until it becomes the last proof that a moment happened." },
      { label: "", title: "How to join?", body: "Follow the archive, log the latest receipt, and submit your wallet through the VCR terminal." },
      { label: "", title: "When reveal?", body: "The sealed files open after mint, one archive slip at a time." }
    ]
  },
  catalog: {
    kicker: "",
    title: "The Things Left Behind",
    intro: "Every store series holds its own language. Six closed doors, and what they left on the counter.",
    cards: [
      { label: "Midnight Diner", title: "Black Coffee. Table 7.", body: "Two cups. Night shift. Someone left before sunrise. The receipt kept the stain." },
      { label: "Night Owl Video", title: "VHS Rental. Late Fee.", body: "Be kind rewind. The tape was never returned. The final broadcast still owes time." },
      { label: "Lucky 8 Gas & Motel", title: "Full Tank. Room 8.", body: "Highway 8. One night. Paid cash. The key was never returned to the front desk." },
      { label: "Side B Records", title: "Used LP. Last Copy.", body: "Basement level. Cat. No. B-0222. All sales are final. The B-side still plays." },
      { label: "Sunset Mart", title: "Cashier 03. 11:47 PM.", body: "Lost change. Candy bar. The store closed on May 31. The receipt survived." },
      { label: "Token Pawn", title: "Broken Watch. Ring Box.", body: "Hold 30 days. Claim check expired. The silver locket was never picked up." }
    ]
  }
};

const counterFileDisplay = document.getElementById("counterFileDisplay");
const counterFileKicker = document.getElementById("counterFileKicker");
const counterFileTitle = document.getElementById("counterFileTitle");
const counterFileIntro = document.getElementById("counterFileIntro");
const counterFileCards = document.getElementById("counterFileCards");
const counterTriggers = document.querySelectorAll(".counter-trigger[data-counter-file]");

function setActiveTab(fileKey) {
  counterTriggers.forEach((trigger) => {
    const active = trigger.dataset.counterFile === fileKey;
    trigger.classList.toggle("is-active", active);
    trigger.setAttribute("aria-expanded", active ? "true" : "false");
  });
}

function renderCounterFile(fileKey, scroll = true) {
  const file = counterFiles[fileKey];
  if (!file || !counterFileDisplay || !counterFileCards) return;
  counterFileKicker.textContent = file.kicker;
  counterFileTitle.textContent = file.title;
  counterFileIntro.textContent = file.intro;
  counterFileCards.innerHTML = file.cards.map((card) => `
    <article class="panel-card">
      ${card.label ? `<span class="panel-card-label">${card.label}</span>` : ""}
      <h2>${card.title}</h2>
      <p>${card.body}</p>
    </article>
  `).join("");
  counterFileDisplay.classList.add("is-active");
  counterFileDisplay.classList.remove("is-hidden");
  setActiveTab(fileKey);
  if (scroll) counterFileDisplay.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function switchPanel(fileKey, scroll = true) {
  renderCounterFile(fileKey, scroll);
}

counterTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => switchPanel(trigger.dataset.counterFile, true));
});

// 页面加载时默认显示 Recovered Notes，不自动滚动
document.addEventListener("DOMContentLoaded", () => {
  switchPanel("notes", false);
});
