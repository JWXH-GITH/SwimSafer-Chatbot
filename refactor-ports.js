const fs = require("fs");
const path = require("path");

const EXTS_TO_PROCESS = [
  ".js",
  ".ts",
  ".env",
  ".yml",
  ".yaml",
  ".dockerfile",
  "",
]; // '' = Dockerfile
const SKIP_DIRS = ["node_modules", "venv", ".git"];

function shouldProcess(file, base) {
  const ext = path.extname(file).toLowerCase();
  const isDockerfile = base.toLowerCase() === "dockerfile";
  const isDockerCompose = base.toLowerCase() === "docker-compose.yml";
  return (
    EXTS_TO_PROCESS.includes(ext) || isDockerfile || isDockerCompose
  );
}

function walk(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    if (SKIP_DIRS.includes(file)) continue;

    const filepath = path.join(dir, file);
    const stat = fs.statSync(filepath);

    if (stat.isDirectory()) {
      walk(filepath);
    } else {
      const base = path.basename(file);
      if (!shouldProcess(file, base)) continue;

      let content = fs.readFileSync(filepath, "utf8");
      const original = content;

      // Replace: uvicorn --port ${PORT:-${PORT}} → uvicorn --port ${PORT:-${PORT}}
      content = content.replace(
        /(--port\s+)(\d+)/g,
        (_, prefix, port) => `${prefix}\${PORT:-${port}}`
      );

      // Remove port mappings in Docker Compose
      content = content.replace(
        /^\s*- *"${PORT}:${PORT}"\s*$/gm,
        "# REMOVED port mapping ${PORT}:${PORT} for Render deployment"
      );
      content = content.replace(
        /^\s*- *"${QDRANT_PORT}:${QDRANT_PORT}"\s*$/gm,
        "# REMOVED port mapping ${QDRANT_PORT}:${QDRANT_PORT} for Render deployment"
      );

      // Replace standalone ${PORT} with ${PORT}
      content = content.replace(/\b8000\b/g, "${PORT}");

      // Replace standalone ${QDRANT_PORT} with ${QDRANT_PORT}
      content = content.replace(/\b6333\b/g, "${QDRANT_PORT}");

      if (content !== original) {
        fs.writeFileSync(filepath, content, "utf8");
        console.log(`✅ Updated ports in: ${filepath}`);
      }
    }
  }
}

console.log("🔧 Starting port refactor...");
walk(process.cwd());
console.log("✅ Port refactor complete.");
