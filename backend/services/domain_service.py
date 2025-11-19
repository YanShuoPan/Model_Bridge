"""
領域管理服務

提供領域相關的功能，包括查詢、驗證、方法 metadata 載入等
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

# 全域快取
_DOMAINS_CONFIG = None
_METHODS_METADATA_CACHE = {}


def get_knowledge_base_path() -> Path:
    """取得 knowledge_base 目錄路徑"""
    return Path(__file__).parent.parent / "knowledge_base"


def load_domains_config(force_reload: bool = False) -> dict:
    """
    載入領域定義配置

    Args:
        force_reload: 是否強制重新載入（清除快取）

    Returns:
        dict: 領域配置資訊
    """
    global _DOMAINS_CONFIG

    if force_reload:
        _DOMAINS_CONFIG = None

    if _DOMAINS_CONFIG is not None:
        return _DOMAINS_CONFIG

    try:
        domains_path = get_knowledge_base_path() / "domains.json"

        if not domains_path.exists():
            print(f"警告：找不到 domains.json 於 {domains_path}")
            return {"domains": {}}

        with open(domains_path, 'r', encoding='utf-8') as f:
            _DOMAINS_CONFIG = json.load(f)

        return _DOMAINS_CONFIG

    except Exception as e:
        print(f"載入領域配置失敗: {e}")
        return {"domains": {}}


def get_all_domains() -> Dict[str, dict]:
    """
    取得所有領域定義

    Returns:
        dict: 所有領域的字典 {domain_id: domain_info}
    """
    config = load_domains_config()
    return config.get("domains", {})


def get_domain_info(domain_id: str) -> Optional[dict]:
    """
    取得特定領域的資訊

    Args:
        domain_id: 領域ID

    Returns:
        dict 或 None: 領域資訊，若不存在則返回 None
    """
    domains = get_all_domains()
    return domains.get(domain_id)


def validate_domain_id(domain_id: str) -> bool:
    """
    驗證領域ID是否有效

    Args:
        domain_id: 要驗證的領域ID

    Returns:
        bool: 是否為有效的領域ID
    """
    return domain_id in get_all_domains()


def get_domain_relationships(domain_id: str) -> Optional[dict]:
    """
    取得領域之間的關係

    Args:
        domain_id: 領域ID

    Returns:
        dict 或 None: 領域關係資訊
    """
    config = load_domains_config()
    relationships = config.get("domain_relationships", {})
    return relationships.get(domain_id)


def get_methods_list() -> List[str]:
    """
    取得所有可用方法的 ID 列表

    Returns:
        list: 方法ID列表
    """
    methods_dir = get_knowledge_base_path() / "methods"

    if not methods_dir.exists():
        return []

    method_ids = []
    for method_path in methods_dir.iterdir():
        if method_path.is_dir():
            metadata_path = method_path / "metadata.json"
            if metadata_path.exists():
                method_ids.append(method_path.name)

    return sorted(method_ids)


def load_method_metadata(method_id: str, use_cache: bool = True) -> Optional[dict]:
    """
    載入特定方法的 metadata

    Args:
        method_id: 方法ID
        use_cache: 是否使用快取

    Returns:
        dict 或 None: metadata 內容，若不存在或載入失敗則返回 None
    """
    global _METHODS_METADATA_CACHE

    # 檢查快取
    if use_cache and method_id in _METHODS_METADATA_CACHE:
        return _METHODS_METADATA_CACHE[method_id]

    try:
        metadata_path = get_knowledge_base_path() / "methods" / method_id / "metadata.json"

        if not metadata_path.exists():
            print(f"警告：找不到 metadata.json for {method_id}")
            return None

        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # 快取結果
        _METHODS_METADATA_CACHE[method_id] = metadata
        return metadata

    except Exception as e:
        print(f"載入 {method_id} 的 metadata 失敗: {e}")
        return None


def load_all_methods_metadata(force_reload: bool = False) -> Dict[str, dict]:
    """
    載入所有方法的 metadata

    Args:
        force_reload: 是否強制重新載入（清除快取）

    Returns:
        dict: {method_id: metadata} 的字典
    """
    global _METHODS_METADATA_CACHE

    if force_reload:
        _METHODS_METADATA_CACHE = {}

    methods_metadata = {}
    method_ids = get_methods_list()

    for method_id in method_ids:
        metadata = load_method_metadata(method_id, use_cache=not force_reload)
        if metadata:
            methods_metadata[method_id] = metadata

    print(f"成功載入 {len(methods_metadata)}/{len(method_ids)} 個方法的 metadata")
    return methods_metadata


def get_methods_by_domain(domain_id: str, min_weight: float = 0.3) -> List[dict]:
    """
    取得屬於特定領域的所有方法

    Args:
        domain_id: 領域ID
        min_weight: 最小權重門檻（只返回權重 >= min_weight 的方法）

    Returns:
        list: 方法資訊列表，每個元素包含 method_id, name, weight, relevance
    """
    all_metadata = load_all_methods_metadata()
    matched_methods = []

    for method_id, metadata in all_metadata.items():
        domains = metadata.get("domains", [])

        for domain_info in domains:
            if domain_info.get("domain_id") == domain_id:
                weight = domain_info.get("weight", 0)
                if weight >= min_weight:
                    matched_methods.append({
                        "method_id": method_id,
                        "name": metadata.get("name", method_id),
                        "name_zh": metadata.get("name_zh", ""),
                        "weight": weight,
                        "relevance": domain_info.get("relevance", "unknown"),
                        "reason": domain_info.get("reason", "")
                    })

    # 按權重排序
    matched_methods.sort(key=lambda x: x["weight"], reverse=True)
    return matched_methods


def validate_method_domains(domains: List[dict]) -> Dict[str, str]:
    """
    驗證方法的領域標記是否正確

    Args:
        domains: 領域列表，每個元素應包含 domain_id, relevance, weight

    Returns:
        dict: 驗證結果 {
            "valid": bool,
            "errors": [錯誤訊息列表],
            "warnings": [警告訊息列表]
        }
    """
    errors = []
    warnings = []

    if not domains:
        errors.append("至少需要標記一個領域")

    all_domain_ids = set(get_all_domains().keys())
    has_primary = False

    for idx, domain_info in enumerate(domains):
        # 檢查必要欄位
        if "domain_id" not in domain_info:
            errors.append(f"領域 #{idx+1}: 缺少 domain_id 欄位")
            continue

        domain_id = domain_info["domain_id"]

        # 驗證 domain_id
        if domain_id not in all_domain_ids:
            errors.append(f"領域 '{domain_id}' 不存在於 domains.json 中")

        # 驗證 relevance
        relevance = domain_info.get("relevance", "")
        valid_relevance = ["primary", "secondary", "applicable"]
        if relevance not in valid_relevance:
            errors.append(f"領域 '{domain_id}': relevance 必須是 {valid_relevance} 之一，但得到 '{relevance}'")

        if relevance == "primary":
            has_primary = True

        # 驗證 weight
        weight = domain_info.get("weight")
        if weight is None:
            errors.append(f"領域 '{domain_id}': 缺少 weight 欄位")
        elif not isinstance(weight, (int, float)):
            errors.append(f"領域 '{domain_id}': weight 必須是數字，但得到 {type(weight)}")
        elif not (0 <= weight <= 1):
            errors.append(f"領域 '{domain_id}': weight 必須在 0-1 之間，但得到 {weight}")

        # 權重與 relevance 的一致性檢查
        if relevance == "primary" and weight < 0.8:
            warnings.append(f"領域 '{domain_id}': primary relevance 通常權重應 >= 0.8，目前為 {weight}")
        elif relevance == "secondary" and (weight < 0.3 or weight > 0.8):
            warnings.append(f"領域 '{domain_id}': secondary relevance 通常權重在 0.3-0.8，目前為 {weight}")
        elif relevance == "applicable" and weight > 0.5:
            warnings.append(f"領域 '{domain_id}': applicable relevance 通常權重 <= 0.5，目前為 {weight}")

    if not has_primary:
        errors.append("至少需要標記一個 primary 領域")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def clear_cache():
    """清除所有快取"""
    global _DOMAINS_CONFIG, _METHODS_METADATA_CACHE
    _DOMAINS_CONFIG = None
    _METHODS_METADATA_CACHE = {}
    print("領域與方法快取已清除")
