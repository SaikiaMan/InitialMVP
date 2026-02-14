let timeline = [];
let svgLoaded = false;
let timers = [];
let lessons = [];
let currentLessonFile = null;

function loadLesson(lessonFile) {
  if (!lessonFile) return;
  currentLessonFile = lessonFile;
  svgLoaded = false;
  document.getElementById("caption").innerText = "Loading…";
  document.getElementById("visual").innerHTML = "";

  const url = lessonFile.startsWith("/") ? lessonFile : "/scenes/" + lessonFile;
  fetch(url)
    .then((res) => {
      if (!res.ok) throw new Error("Lesson failed: " + res.status);
      return res.json();
    })
    .then((data) => {
      const svgPath = data.svg?.startsWith("/") ? data.svg : "/" + (data.svg || "").replace(/^\.\.\//, "");
      return fetch(svgPath)
        .then((r) => {
          if (!r.ok) throw new Error("SVG failed: " + r.status);
          return r.text();
        })
        .then((svgText) => {
          document.getElementById("visual").innerHTML = svgText;
          timeline = data.timeline || [];
          svgLoaded = true;
          document.getElementById("caption").innerText = "Ready. Press Play.";
        });
    })
    .catch((e) => {
      console.error(e);
      document.getElementById("caption").innerText = "Failed to load: " + e.message;
    });
}

function initLessons() {
  const selector = document.getElementById("lesson-select");
  fetch("/scenes/index.json")
    .then((res) => res.ok ? res.json() : { lessons: [] })
    .then((data) => {
      lessons = data.lessons || [];
      if (lessons.length === 0) {
        loadLesson("stack_lesson.json");
        return;
      }
      selector.innerHTML = "";
      lessons.forEach((entry, i) => {
        const opt = document.createElement("option");
        opt.value = entry.file;
        opt.textContent = entry.name;
        opt.selected = i === 0;
        selector.appendChild(opt);
      });
      selector.hidden = false;
      loadLesson(lessons[0].file);
    })
    .catch(() => {
      loadLesson("stack_lesson.json");
    });

  selector.addEventListener("change", () => {
    const file = selector.value;
    if (file) loadLesson(file);
  });
}

function play() {
  if (!svgLoaded) {
    document.getElementById("caption").innerText = "SVG not loaded yet.";
    return;
  }
  reset();
  timeline.forEach((step) => {
    const timer = setTimeout(() => {
      const el = document.getElementById(step.target);
      if (!el) return;

      if (step.action === "show") el.style.display = "block";
      if (step.action === "hide") el.style.display = "none";
      if (step.action === "move") {
        const dx = step.x !== undefined ? step.x : 0;
        const dy = step.y !== undefined ? step.y : 0;
        el.setAttribute("transform", `translate(${dx}, ${dy})`);
      }
      if (step.action === "highlight") {
        el.style.stroke = step.color || "orange";
        el.style.strokeWidth = "3";
        el.classList.add("highlight");
      }
      const caption = document.getElementById("caption");
      if (caption && step.description) caption.innerText = step.description;
    }, step.t * 1000);
    timers.push(timer);
  });
}

function reset() {
  timers.forEach((t) => clearTimeout(t));
  timers = [];
  const svg = document.getElementById("visual");
  if (!svg) return;
  svg.querySelectorAll("*").forEach((el) => {
    el.style.display = "";
    el.style.stroke = "";
    el.style.strokeWidth = "";
    el.classList.remove("highlight");
    el.removeAttribute("transform");
  });
  document.getElementById("caption").innerText = "Press Play";
}

document.getElementById("btn-play")?.addEventListener("click", play);
document.getElementById("btn-reset")?.addEventListener("click", reset);

const sel = document.getElementById("lesson-select");
if (sel) {
  sel.hidden = true;
  initLessons();
} else {
  loadLesson("stack_lesson.json");
}
