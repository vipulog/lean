// Configure marked with highlight.js integration
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (err) {
        console.warn("Highlight.js error:", err);
      }
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true, // Convert \n to <br>
  gfm: true, // GitHub Flavored Markdown
});

function renderMath() {
  renderMathInElement(document.getElementById("content"), {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false },
    ],
  });
}

function displayRenderError(content) {
  document.getElementById("content").innerHTML = `
    <div class="error">
      <strong>Rendering Error:</strong> ${error.message}
      <pre>${content}</pre>
    </div>
  `;
}

function renderContent(content) {
  try {
    let htmlContent = marked.parse(content);
    document.getElementById("content").innerHTML = htmlContent;
    renderMath();
    document.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });
  } catch (error) {
    console.error("Rendering error:", error);
    displayRenderError(content);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const contentDiv = document.getElementById("content");
  if (contentDiv.textContent.trim() === "CONTENT") {
    contentDiv.innerHTML = '<div class="loading">Waiting for content...</div>';
  } else {
    const initialContent = contentDiv.textContent;
    renderContent(initialContent);
  }
});
