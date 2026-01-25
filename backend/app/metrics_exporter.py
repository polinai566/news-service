import json
import os
import asyncio
from datetime import datetime
from typing import Dict, Any
from prometheus_client import REGISTRY
from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    HistogramMetricFamily,
    SummaryMetricFamily
)


def collect_metrics_to_dict() -> Dict[str, Any]:
    metrics_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": []
    }
    
    try:
        # официальный API для сбора метрик из registry
        for metric_family in REGISTRY.collect():
            metric_info = {
                "name": metric_family.name,
                "type": metric_family.type,
                "help": metric_family.documentation,
                "samples": []
            }
            
            # тип метрики
            if isinstance(metric_family, CounterMetricFamily):
                metric_info["type"] = "counter"
            elif isinstance(metric_family, GaugeMetricFamily):
                metric_info["type"] = "gauge"
            elif isinstance(metric_family, HistogramMetricFamily):
                metric_info["type"] = "histogram"
            elif isinstance(metric_family, SummaryMetricFamily):
                metric_info["type"] = "summary"
            
            # извлечение samples (значения метрик с labels)
            for sample in metric_family.samples:
                sample_data = {
                    "labels": dict(sample.labels) if sample.labels else {},
                    "value": float(sample.value)
                }
                # добавление дополнительной информации о типе sample
                if sample.name.endswith("_bucket") or sample.name.endswith("_count") or sample.name.endswith("_sum"):
                    sample_data["sample_name"] = sample.name
                metric_info["samples"].append(sample_data)
            
            if metric_info["samples"]:
                metrics_data["metrics"].append(metric_info)
                
    except Exception as e:
        print(f"Ошибка при сборе метрик: {e}")
    
    return metrics_data


def save_metrics_to_file(metrics_dir: str = "metrics", max_files: int = 10) -> str:
    # создание директории, если её нет
    os.makedirs(metrics_dir, exist_ok=True)
    
    # сбор метрик метрики
    metrics_data = collect_metrics_to_dict()
    
    # формирование имени файла с timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"metrics_{timestamp}.json"
    filepath = os.path.join(metrics_dir, filename)
    
    # сохранение в JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)
    
    # ротация файлов: удаляем старые, если их больше max_files
    try:
        files = sorted(
            [f for f in os.listdir(metrics_dir) if f.startswith("metrics_") and f.endswith(".json")],
            key=lambda x: os.path.getmtime(os.path.join(metrics_dir, x)),
            reverse=True
        )
        # удаление старых файлов
        for old_file in files[max_files:]:
            old_filepath = os.path.join(metrics_dir, old_file)
            try:
                os.remove(old_filepath)
            except Exception:
                pass
    except Exception:
        pass
    
    return filepath


async def metrics_exporter_task(interval_seconds: int = 300, metrics_dir: str = "metrics"):
    while True:
        try:
            filepath = save_metrics_to_file(metrics_dir=metrics_dir)
            print(f"Метрики сохранены в {filepath}")
        except Exception as e:
            print(f"Ошибка при сохранении метрик: {e}")
        await asyncio.sleep(interval_seconds)

