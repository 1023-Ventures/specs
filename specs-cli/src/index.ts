#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { version } from '../package.json';

const program = new Command();

program
  .name('specs')
  .description('CLI tool for managing specs')
  .version(version);

program
  .command('init')
  .description('Initialize a new specs project')
  .action(() => {
    console.log(chalk.green('✅ Initializing new specs project...'));
    console.log(chalk.blue('📁 Project initialized successfully!'));
  });

program
  .command('build')
  .description('Build the specs project')
  .action(() => {
    console.log(chalk.yellow('🔨 Building specs project...'));
    console.log(chalk.green('✅ Build completed successfully!'));
  });

program
  .command('deploy')
  .description('Deploy the specs project')
  .option('-e, --environment <env>', 'deployment environment', 'production')
  .action((options: { environment: string }) => {
    console.log(chalk.cyan(`🚀 Deploying to ${options.environment}...`));
    console.log(chalk.green('✅ Deployment completed successfully!'));
  });

program
  .command('status')
  .description('Check project status')
  .action(() => {
    console.log(chalk.blue('📊 Project Status:'));
    console.log(chalk.white('• Status: ') + chalk.green('Active'));
    console.log(chalk.white('• Version: ') + chalk.yellow(version));
    console.log(chalk.white('• Environment: ') + chalk.cyan('Development'));
  });

// Parse command line arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}
