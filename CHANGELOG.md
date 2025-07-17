# Changelog

All notable changes to the TexIV project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **rich 集成**: 引入 rich 库，提供现代化的终端界面和丰富的进度显示
  - 实时进度条，避免程序"卡住"的错觉
  - 彩色日志输出，不同级别日志使用不同颜色区分
  - 表格化结果显示，更清晰展示数据
  - 语法高亮的代码块显示
  - 旋转加载动画，实时反馈处理状态
  - 新增 `--verbose` 命令行参数启用详细输出模式
- **增强的用户体验**: 所有长时间运行任务都有明确的进度指示和剩余时间估计
- **智能状态面板**: 实时显示当前处理步骤、已用时间和预计剩余时间

### Changed
- 优化 CLI 输出格式，提供更清晰的状态信息
- 改进错误处理和用户反馈机制

### Fixed
- 修复长时间运行任务无反馈导致用户误以为程序卡死的问题
- 修复网络请求超时无提示的问题

## [0.1.9] - 2025-07-17

### Added
- 基础文本到工具变量转换功能
- CLI 命令行接口支持
- 支持多种中文分词器集成
- 内置停用词过滤功能
- Stata 插件支持 (.ado 和 .sthlp 文件)

### Changed
- 优化核心算法性能
- 改进配置文件结构

### Fixed
- 修复多个平台兼容性问题
- 修正测试用例中的路径问题

## [0.1.0] - 2025-07-16

### Added
- 项目初始版本
- 基本项目结构和依赖配置
- 核心功能框架搭建