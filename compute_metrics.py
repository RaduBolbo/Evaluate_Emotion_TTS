import os
import json
from glob import glob
from statistics import mean
from collections import defaultdict

def compute_naturalness_per_model(filepath):
    with open(filepath, encoding='utf-8') as f:
        try:
            data = json.load(f)
            raw_responses = data.get("responses", {}).get("naturalness", [])
            model_scores = defaultdict(list)
            for x in raw_responses:
                model = x.get("model")
                score = x.get("score")
                if model is not None and isinstance(score, (int, float)):
                    model_scores[model].append(score)
            return {model: mean(scores) for model, scores in model_scores.items()}
        except Exception as e:
            print(f"❌ Error parsing {filepath}: {e}")
            return {}
def compute_accuracy_per_model(filepath):
    with open(filepath) as f:
        try:
            data = json.load(f)
            model_flags = defaultdict(list)
            for x in data.get('responses', []):
                model = x.get('model')
                correct = x.get('correct')
                if model is not None and isinstance(correct, bool):
                    model_flags[model].append(correct)
            return {model: mean(flags) for model, flags in model_flags.items() if flags}
        except Exception as e:
            print(f"❌ Error parsing {filepath}: {e}")
            return {}

def main(input_dir):
    suffix_to_metric_fn = {
        'naturalness': compute_naturalness_per_model,
        'EDT': compute_accuracy_per_model,
        'EIT': compute_accuracy_per_model,
        'EST': compute_accuracy_per_model,
        'EDiT': compute_accuracy_per_model,
    }

    final_results = defaultdict(lambda: defaultdict(list))

    for suffix, metric_fn in suffix_to_metric_fn.items():
        pattern = os.path.join(input_dir, f"*{suffix}.json")
        files = glob(pattern)
        if not files:
            print(f"ℹ️ No files found for *{suffix}.json")
        for file in files:
            model_scores = metric_fn(file)
            for model, score in model_scores.items():
                final_results[suffix][model].append(score)
            print(f"✅ Processed {os.path.basename(file)} ({suffix}) → models: {list(model_scores.keys())}")

    print("\n=== 📊 Final Averaged Metrics Per Model ===")
    for metric, model_dict in final_results.items():
        print(f"\n▶ {metric}")
        for model, scores in sorted(model_dict.items()):
            avg = mean(scores)
            print(f"  {model}: {avg:.3f}")

if __name__ == "__main__":
    main('results')
