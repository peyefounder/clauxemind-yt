#!/usr/bin/env bun
/**
 * CLAUXEMIND-YT — Terminal Command Executor
 * 
 * Execute ANY terminal command, install packages, manage projects.
 * 
 * Usage:
 *   bun index.ts                    — Start interactive REPL mode
 *   bun index.ts "command here"     — Execute single command
 *   bun index.ts --help             — Show help
 *   bun index.ts --version          — Show version
 * 
 * @author CLAUXEMIND
 */

import { spawn } from "bun";
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, statSync, rmSync } from "fs";
import { join, resolve } from "path";
import { homedir } from "os";

const VERSION = "1.0.0";
const APP_NAME = "CLAUXEMIND-YT";
const HISTORY_FILE = join(homedir(), ".clauxemind-yt-history");
const MAX_HISTORY = 100;

const c = {
  reset: "\x1b[0m", bold: "\x1b[1m", dim: "\x1b[2m",
  red: "\x1b[31m", green: "\x1b[32m", yellow: "\x1b[33m",
  blue: "\x1b[34m", magenta: "\x1b[35m", cyan: "\x1b[36m",
  white: "\x1b[37m", gray: "\x1b[90m",
};

let history: string[] = [];
let cwd = process.cwd();

function loadHistory(): string[] {
  try { if (existsSync(HISTORY_FILE)) return JSON.parse(readFileSync(HISTORY_FILE, "utf-8")); } catch {}
  return [];
}

function saveHistory(cmd: string) {
  history.push(cmd);
  if (history.length > MAX_HISTORY) history = history.slice(-MAX_HISTORY);
  try { writeFileSync(HISTORY_FILE, JSON.stringify(history)); } catch {}
}

function printBanner() {
  console.log(`${c.cyan}${c.bold}
  ╔══════════════════════════════════════════════╗
  ║  ${c.white}CLAUXEMIND-YT${c.cyan}  v${VERSION}                  ║
  ║  Terminal Command Executor                    ║
  ║  Execute • Install • Manage • Everything      ║
  ╚══════════════════════════════════════════════╝
  ${c.gray}Type 'help' for commands • 'exit' to quit${c.reset}
  ${c.dim}cwd: ${cwd}${c.reset}
`);
}

function log(msg: string, color: string = c.reset) { console.log(`${color}${msg}${c.reset}`); }
function error(msg: string) { console.error(`${c.red}✗ ${msg}${c.reset}`); }
function success(msg: string) { console.log(`${c.green}✓ ${msg}${c.reset}`); }
function info(msg: string) { console.log(`${c.cyan}ℹ ${msg}${c.reset}`); }

function parseTokens(line: string): string[] {
  const tokens: string[] = [];
  let current = "", inQuote = false, quoteChar = "";
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if ((ch === '"' || ch === "'") && !inQuote) { inQuote = true; quoteChar = ch; }
    else if (ch === quoteChar && inQuote) { inQuote = false; quoteChar = ""; }
    else if (ch === " " && !inQuote) { if (current) { tokens.push(current); current = ""; } }
    else current += ch;
  }
  if (current) tokens.push(current);
  return tokens;
}

async function execExternal(cmd: string, args: string[]): Promise<number> {
  log(`\n${c.gray}$ ${cmd} ${args.join(" ")}${c.reset}`);
  try {
    const proc = spawn({ cmd: [cmd, ...args], cwd, stdout: "inherit", stderr: "inherit", stdin: "inherit", env: { ...process.env, FORCE_COLOR: "1" } });
    return await proc.exited;
  } catch (e: any) { error(`Failed: ${e?.message || e}`); return 1; }
}

async function execute(line: string): Promise<number> {
  const tokens = parseTokens(line);
  if (tokens.length === 0) return 0;
  const [cmd, ...args] = tokens;

  switch (cmd) {
    case "exit": case "quit": log("\nGoodbye! 👋", c.cyan); process.exit(0);
    case "help": showHelp(); return 0;
    case "clear": case "cls": console.clear(); return 0;
    case "cd":
      if (args[0]) { const p = resolve(cwd, args[0]); if (existsSync(p)) { cwd = p; process.chdir(cwd); } else { error(`Not found: ${p}`); return 1; } }
      return 0;
    case "pwd": log(cwd); return 0;
    case "history": history.forEach((h, i) => log(`  ${c.gray}${i + 1}${c.reset}  ${h}`)); return 0;
    case "install": case "i": return handleInstall(args);
    case "run": return handleRun(args);
    case "list": case "ls": return handleList(args);
    case "version": case "v": log(`${APP_NAME} v${VERSION} • Bun ${Bun.version} • Node ${process.version}`); return 0;
    case "whoami": log(process.env.USER || "unknown"); return 0;
    case "env": Object.entries(process.env).forEach(([k, v]) => log(`${c.cyan}${k}${c.reset}=${c.gray}${v}${c.reset}`)); return 0;
    case "echo": log(args.join(" ")); return 0;
    case "mkdir": args.forEach((d) => { try { mkdirSync(resolve(cwd, d), { recursive: true }); success(`Created: ${d}`); } catch (e: any) { error(`${d}: ${e?.message}`); } }); return 0;
    case "cat": args.forEach((f) => { try { log(readFileSync(resolve(cwd, f), "utf-8")); } catch { error(`Not found: ${f}`); } }); return 0;
    case "touch": args.forEach((f) => { const fp = resolve(cwd, f); if (!existsSync(fp)) writeFileSync(fp, ""); }); return 0;
    case "rm": {
      const force = args.includes("-f") || args.includes("--force") || args.includes("-rf");
      const recursive = args.includes("-r") || args.includes("-rf") || args.includes("-R");
      args.filter((a) => !a.startsWith("-")).forEach((f) => { try { rmSync(resolve(cwd, f), { recursive, force }); success(`Removed: ${f}`); } catch (e: any) { if (!force) error(`${f}: ${e?.message}`); } });
      return 0;
    }
    case "export": case "set": args.forEach((a) => { const [k, ...v] = a.split("="); if (k) process.env[k] = v.join("="); }); return 0;
    default: return execExternal(cmd, args);
  }
}

function detectPM(): string {
  if (existsSync(join(cwd, "bun.lock"))) return "bun";
  if (existsSync(join(cwd, "pnpm-lock.yaml"))) return "pnpm";
  if (existsSync(join(cwd, "yarn.lock"))) return "yarn";
  return "npm";
}

async function handleInstall(args: string[]): Promise<number> {
  const pm = detectPM();
  if (args.length === 0 || args[0].startsWith("-")) {
    info(`Installing deps with ${pm}...`);
    return execExternal(pm, ["install"]);
  }
  const dev = args.includes("-D") || args.includes("--dev");
  const pkgs = args.filter((a) => !a.startsWith("-"));
  const cmdArgs = pm === "npm" ? ["install", ...pkgs, ...(dev ? ["--save-dev"] : [])] : ["add", ...pkgs, ...(dev ? ["--dev"] : [])];
  info(`Installing: ${pkgs.join(", ")} (${dev ? "dev" : "prod"}) with ${pm}...`);
  return execExternal(pm, cmdArgs);
}

async function handleRun(args: string[]): Promise<number> {
  if (!args[0]) { error("Usage: run <script>"); return 1; }
  const pm = detectPM();
  info(`Running: ${args[0]}...`);
  return execExternal(pm, pm === "npm" ? ["run", args[0]] : ["run", args[0]]);
}

async function handleList(args: string[]): Promise<number> {
  const target = args[0] || cwd;
  try {
    readdirSync(target).forEach((item) => {
      try { const s = statSync(join(target, item)); s.isDirectory() ? log(`  ${c.blue}${c.bold}${item}/${c.reset}`) : log(`  ${c.white}${item}${c.reset}  ${c.gray}${(s.size / 1024).toFixed(1)}KB${c.reset}`); }
      catch { log(`  ${c.gray}${item}${c.reset}`); }
    });
    return 0;
  } catch { error(`Cannot list: ${target}`); return 1; }
}

function showHelp() {
  log(`
${c.bold}${c.cyan}CLAUXEMIND-YT — Commands${c.reset}

${c.yellow}Built-in:${c.reset}
  ${c.green}help${c.reset}              Show help          ${c.green}exit${c.reset}            Quit
  ${c.green}clear${c.reset}             Clear screen       ${c.green}cd <dir>${c.reset}        Change directory
  ${c.green}pwd${c.reset}               Working dir        ${c.green}ls${c.reset}              List files
  ${c.green}cat <file>${c.reset}        Read file          ${c.green}touch <file>${c.reset}    Create file
  ${c.green}mkdir <dir>${c.reset}       Create dir         ${c.green}rm <file>${c.reset}       Remove (-rf recursive)
  ${c.green}echo <text>${c.reset}       Print text         ${c.green}env${c.reset}             Show env vars
  ${c.green}export K=V${c.reset}        Set env var        ${c.green}whoami${c.reset}          Current user
  ${c.green}history${c.reset}           Show history       ${c.green}version${c.reset}         Version info

${c.yellow}Package Management:${c.reset}
  ${c.green}install [pkg]${c.reset}     Install (auto bun/npm/pnpm/yarn)
  ${c.green}install -D <pkg>${c.reset}  Install dev dependency
  ${c.green}run <script>${c.reset}      Run package.json script

${c.yellow}System Commands (all pass-through):${c.reset}
  ${c.gray}git, npm, bun, python, docker, curl, wget, pip, cargo, go,${c.reset}
  ${c.gray}rustc, make, ssh, scp, tar, chmod, grep, find, sed, awk, etc.${c.reset}

${c.yellow}Examples:${c.reset}
  ${c.dim}bun index.ts "git status"${c.reset}
  ${c.dim}bun index.ts "npm install express"${c.reset}
  ${c.dim}bun index.ts "docker build -t app ."${c.reset}
  ${c.dim}bun index.ts "python script.py"${c.reset}
  ${c.dim}bun index.ts "curl https://api.example.com"${c.reset}
  ${c.dim}bun index.ts "pip install flask"${c.reset}

${c.yellow}Tips:${c.reset}
  ${c.gray}• Chain: mkdir test && cd test${c.reset}
  ${c.gray}• Quotes for spaces: cd "My Documents"${c.reset}
`);
}

async function main() {
  printBanner();
  history = loadHistory();
  const args = process.argv.slice(2);

  // Single command mode
  if (args.length > 0) {
    const cmd = args.join(" ");
    if (cmd === "--help" || cmd === "-h") { showHelp(); process.exit(0); }
    if (cmd === "--version" || cmd === "-v") { log(`${APP_NAME} v${VERSION}`); process.exit(0); }
    log(`${c.cyan}Executing: ${cmd}${c.reset}`);
    // Handle && chaining
    if (cmd.includes("&&")) {
      for (const part of cmd.split("&&").map((s) => s.trim())) {
        if (part) { const code = await execute(part); if (code !== 0) { error(`Exit code ${code}`); process.exit(code); } }
      }
      process.exit(0);
    }
    const code = await execute(cmd);
    process.exit(code);
  }

  // Interactive REPL mode
  log(`${c.gray}Interactive mode — type commands and press Enter${c.reset}\n`);
  const prompt = () => process.stdout.write(`${c.cyan}clauxemind-yt${c.reset} ${c.gray}>${c.reset} `);
  prompt();

  for await (const line of console) {
    const trimmed = line.trim();
    if (trimmed) {
      saveHistory(trimmed);
      if (trimmed.includes("&&")) {
        for (const part of trimmed.split("&&").map((s) => s.trim())) {
          if (part) { const code = await execute(part); if (code !== 0) { error(`Exit code ${code}`); break; } }
        }
      } else {
        await execute(trimmed);
      }
    }
    prompt();
  }
}

main().catch((e) => { error(`Fatal: ${e?.message || e}`); process.exit(1); });
