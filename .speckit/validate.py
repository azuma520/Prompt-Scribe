#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt-Scribe 架構規範驗證工具

用途: 自動檢查專案是否符合 PROJECT_STRUCTURE.md 定義的架構規範
版本: V1.0.0
日期: 2025-10-15
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
import re

# 設置 Windows 控制台 UTF-8 編碼
if sys.platform == 'win32':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

class ArchitectureValidator:
    """架構驗證器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / ".speckit" / "config.yaml"
        self.config = self._load_config()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []
        
    def _load_config(self) -> Dict:
        """載入配置文件"""
        if not self.config_path.exists():
            print(f"❌ 配置文件不存在: {self.config_path}")
            sys.exit(1)
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def validate_directory_structure(self) -> bool:
        """驗證目錄結構"""
        print("\n🔍 檢查目錄結構...")
        
        required_dirs = self.config['structure']['required_directories']
        all_valid = True
        
        for dir_spec in required_dirs:
            dir_path = self.project_root / dir_spec['path']
            
            if not dir_path.exists():
                self.errors.append(
                    f"缺少必要目錄: {dir_spec['path']} ({dir_spec['purpose']})"
                )
                all_valid = False
            else:
                self.passed.append(f"✓ 目錄存在: {dir_spec['path']}")
                
                # 檢查子目錄
                if 'subdirectories' in dir_spec:
                    for subdir in dir_spec['subdirectories']:
                        subdir_path = dir_path / subdir
                        if not subdir_path.exists():
                            self.warnings.append(
                                f"建議子目錄缺失: {dir_spec['path']}/{subdir}"
                            )
        
        return all_valid
    
    def validate_core_services(self) -> bool:
        """驗證核心服務文件"""
        print("\n🔍 檢查核心服務...")
        
        services_dir = self.project_root / "src" / "api" / "services"
        all_valid = True
        
        if not services_dir.exists():
            self.errors.append("服務目錄不存在: src/api/services/")
            return False
        
        # 檢查所有版本的服務
        for version_key in ['v1_base', 'v2_p1_optimization', 'v2_p2_advanced']:
            services = self.config['core_services'][version_key]
            
            for service in services:
                service_path = services_dir / service['name']
                
                if not service_path.exists():
                    self.warnings.append(
                        f"服務文件缺失: {service['name']} "
                        f"({service['purpose']}, {service['version']})"
                    )
                else:
                    self.passed.append(
                        f"✓ 服務存在: {service['name']} ({service['version']})"
                    )
        
        return all_valid
    
    def validate_api_routers(self) -> bool:
        """驗證 API 路由"""
        print("\n🔍 檢查 API 路由...")
        
        routers_dir = self.project_root / "src" / "api" / "routers"
        all_valid = True
        
        if not routers_dir.exists():
            self.errors.append("路由目錄不存在: src/api/routers/")
            return False
        
        # 檢查 V1 和 LLM 路由
        for category in ['v1_basic', 'v2_llm']:
            routers = self.config['api_routers'][category]
            
            for router in routers:
                router_path = routers_dir / router['file']
                
                if not router_path.exists():
                    self.warnings.append(
                        f"路由文件缺失: {router['file']} ({router['purpose']})"
                    )
                else:
                    self.passed.append(
                        f"✓ 路由存在: {router['file']} ({router['endpoints']} 端點)"
                    )
        
        return all_valid
    
    def validate_test_coverage(self) -> bool:
        """驗證測試覆蓋"""
        print("\n🔍 檢查測試套件...")
        
        tests_dir = self.project_root / "src" / "api" / "tests"
        all_valid = True
        
        if not tests_dir.exists():
            self.errors.append("測試目錄不存在: src/api/tests/")
            return False
        
        test_suites = self.config['testing']['test_suites']
        
        for suite in test_suites:
            test_path = tests_dir / suite['file']
            
            if not test_path.exists():
                self.warnings.append(
                    f"測試文件缺失: {suite['file']} ({suite['coverage']})"
                )
            else:
                self.passed.append(
                    f"✓ 測試存在: {suite['file']} ({suite['tests']} 測試)"
                )
        
        return all_valid
    
    def validate_documentation(self) -> bool:
        """驗證文檔完整性"""
        print("\n🔍 檢查文檔完整性...")
        
        all_valid = True
        required_files = self.config['documentation']['required_files']
        
        # 檢查根目錄文檔
        for doc_file in required_files['root']:
            doc_path = self.project_root / doc_file
            
            if not doc_path.exists():
                self.errors.append(f"必要文檔缺失: {doc_file}")
                all_valid = False
            else:
                self.passed.append(f"✓ 文檔存在: {doc_file}")
        
        # 檢查 API 文檔
        for doc_file in required_files['api']:
            doc_path = self.project_root / doc_file
            
            if not doc_path.exists():
                self.warnings.append(f"API 文檔缺失: {doc_file}")
            else:
                self.passed.append(f"✓ API 文檔存在: {doc_file}")
        
        return all_valid
    
    def validate_cicd(self) -> bool:
        """驗證 CI/CD 配置"""
        print("\n🔍 檢查 CI/CD 配置...")
        
        workflows_dir = self.project_root / ".github" / "workflows"
        all_valid = True
        
        if not workflows_dir.exists():
            self.warnings.append("CI/CD 目錄不存在: .github/workflows/")
            return True  # 這是可選的
        
        workflows = self.config['cicd']['workflows']
        
        for workflow in workflows:
            workflow_path = workflows_dir / workflow['name']
            
            if not workflow_path.exists():
                self.warnings.append(
                    f"CI/CD 工作流缺失: {workflow['name']} "
                    f"(觸發: {workflow['trigger']})"
                )
            else:
                self.passed.append(
                    f"✓ 工作流存在: {workflow['name']}"
                )
        
        return all_valid
    
    def validate_deployment_configs(self) -> bool:
        """驗證部署配置"""
        print("\n🔍 檢查部署配置...")
        
        all_valid = True
        platforms = self.config['deployment']['platforms']
        
        for platform in platforms:
            if 'config' in platform:
                config_path = self.project_root / platform['config']
                
                if not config_path.exists():
                    self.warnings.append(
                        f"{platform['name']} 配置缺失: {platform['config']}"
                    )
                else:
                    self.passed.append(
                        f"✓ {platform['name']} 配置存在"
                    )
        
        return all_valid
    
    def validate_naming_conventions(self) -> bool:
        """驗證命名規範"""
        print("\n🔍 檢查命名規範...")
        
        services_dir = self.project_root / "src" / "api" / "services"
        all_valid = True
        
        if services_dir.exists():
            for file_path in services_dir.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                    
                # 檢查 snake_case
                if not re.match(r'^[a-z][a-z0-9_]*\.py$', file_path.name):
                    self.warnings.append(
                        f"服務文件命名不符合 snake_case: {file_path.name}"
                    )
                    all_valid = False
        
        return all_valid
    
    def check_forbidden_patterns(self) -> bool:
        """檢查禁止的代碼模式"""
        print("\n🔍 檢查代碼模式...")
        
        forbidden = self.config['code_quality']['forbidden_patterns']
        all_valid = True
        
        # 檢查所有 Python 文件
        for py_file in self.project_root.glob("src/**/*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for pattern_rule in forbidden:
                pattern = pattern_rule['pattern']
                
                # 檢查是否在允許目錄中
                allowed = False
                if 'allowed_in' in pattern_rule:
                    for allowed_path in pattern_rule['allowed_in']:
                        if allowed_path in str(py_file):
                            allowed = True
                            break
                
                if not allowed and pattern in content:
                    self.warnings.append(
                        f"{py_file.relative_to(self.project_root)}: "
                        f"使用了禁止模式 '{pattern}' - {pattern_rule['reason']}"
                    )
        
        return all_valid
    
    def print_report(self):
        """輸出驗證報告"""
        print("\n" + "="*70)
        print("📊 Prompt-Scribe 架構驗證報告")
        print("="*70)
        
        # 統計
        total_checks = len(self.passed) + len(self.warnings) + len(self.errors)
        pass_rate = (len(self.passed) / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n✅ 通過檢查: {len(self.passed)}")
        print(f"⚠️  警告事項: {len(self.warnings)}")
        print(f"❌ 錯誤事項: {len(self.errors)}")
        print(f"📈 通過率: {pass_rate:.1f}%")
        
        # 顯示錯誤
        if self.errors:
            print("\n❌ 嚴重錯誤:")
            for error in self.errors:
                print(f"  • {error}")
        
        # 顯示警告
        if self.warnings:
            print("\n⚠️  警告事項:")
            for warning in self.warnings[:10]:  # 只顯示前 10 個
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... 還有 {len(self.warnings) - 10} 個警告")
        
        # 顯示成功項（僅摘要）
        if self.passed and not self.errors:
            print("\n✅ 主要檢查通過:")
            categories = {}
            for item in self.passed:
                category = item.split(':')[0]
                categories[category] = categories.get(category, 0) + 1
            
            for category, count in categories.items():
                print(f"  {category}: {count} 項")
        
        print("\n" + "="*70)
        
        # 評級
        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("🏆 評級: A+ (完全符合架構規範)")
            return 0
        elif len(self.errors) == 0:
            print("🥈 評級: A (符合核心規範,有改進空間)")
            return 0
        elif len(self.errors) < 5:
            print("⚠️  評級: B (有少量違規,需要修正)")
            return 1
        else:
            print("❌ 評級: C (嚴重違規,必須立即修正)")
            return 2
    
    def run(self) -> int:
        """執行完整驗證"""
        print("🚀 Prompt-Scribe 架構規範驗證")
        print(f"📁 專案路徑: {self.project_root.absolute()}")
        print(f"📋 配置文件: {self.config_path}")
        print(f"📌 專案版本: {self.config['project']['version']}")
        
        # 執行所有驗證
        self.validate_directory_structure()
        self.validate_core_services()
        self.validate_api_routers()
        self.validate_test_coverage()
        self.validate_documentation()
        self.validate_cicd()
        self.validate_deployment_configs()
        self.validate_naming_conventions()
        self.check_forbidden_patterns()
        
        # 輸出報告
        return self.print_report()


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prompt-Scribe 架構規範驗證工具"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="專案根目錄路徑 (預設: 當前目錄)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="嚴格模式: 警告也視為失敗"
    )
    
    args = parser.parse_args()
    
    # 執行驗證
    validator = ArchitectureValidator(args.project_root)
    exit_code = validator.run()
    
    # 嚴格模式
    if args.strict and validator.warnings:
        print("\n⚠️  嚴格模式: 因有警告事項,驗證失敗")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

