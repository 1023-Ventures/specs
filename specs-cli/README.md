# Specs CLI

A TypeScript-based CLI tool for managing specs.

## Installation

```bash
npm install
```

## Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run in development mode
npm run dev

# Watch for changes
npm run watch
```

## Usage

### Development Mode (Recommended)
```bash
# Show help
npm run dev -- --help

# Initialize a new project
npm run dev -- init

# Build project
npm run dev -- build

# Deploy project
npm run dev -- deploy --environment production

# Check status
npm run dev -- status
```

### Global Installation
```bash
# Install globally first
npm install -g .

# Then use directly
specs --help
specs init
specs build
specs deploy --environment production
specs status
```

### Alternative: Using npx
```bash
npx specs --help
npx specs status
```

## Commands

- `init` - Initialize a new specs project
- `build` - Build the specs project
- `deploy` - Deploy the specs project
- `status` - Check project status

## Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Run in development mode with ts-node
- `npm run start` - Run the compiled JavaScript
- `npm run watch` - Watch for changes and recompile
- `npm run clean` - Remove build artifacts
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Project Structure

```
specs-cli/
├── src/
│   └── index.ts       # Main CLI entry point
├── dist/              # Compiled JavaScript (generated)
├── package.json       # Project configuration
├── tsconfig.json      # TypeScript configuration
└── README.md          # This file
```
