#!/usr/bin/env python3
import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_feature_file(filepath):
    features = []
    current_feature = None
    current_scenario = None
    current_tags = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Parse tags
        if line_stripped.startswith('@'):
            current_tags = [t.strip() for t in line_stripped.split() if t.strip()]
            continue
            
        # Parse Feature
        if line_stripped.startswith('Feature:'):
            name = line_stripped[len('Feature:'):].strip()
            current_feature = {
                'name': name,
                'description': '',
                'tags': current_tags,
                'file': filepath,
                'scenarios': [],
                'background': []
            }
            features.append(current_feature)
            current_tags = []
            continue
            
        # Parse Background
        if line_stripped.startswith('Background:'):
            current_scenario = {
                'name': 'Background',
                'type': 'Background',
                'steps': []
            }
            if current_feature:
                current_feature['background'] = current_scenario['steps']
            continue
            
        # Parse Scenario or Scenario Outline
        if line_stripped.startswith('Scenario:') or line_stripped.startswith('Scenario Outline:'):
            is_outline = line_stripped.startswith('Scenario Outline:')
            prefix = 'Scenario Outline:' if is_outline else 'Scenario:'
            name = line_stripped[len(prefix):].strip()
            current_scenario = {
                'name': name,
                'type': 'ScenarioOutline' if is_outline else 'Scenario',
                'tags': current_tags,
                'steps': []
            }
            if current_feature:
                current_feature['scenarios'].append(current_scenario)
            current_tags = []
            continue
            
        # Parse Steps
        step_keywords = ('Given', 'When', 'Then', 'And', 'But')
        matched_step = False
        for kw in step_keywords:
            if line_stripped.startswith(kw + ' '):
                step_text = line_stripped[len(kw):].strip()
                if current_scenario is not None:
                    current_scenario['steps'].append({
                        'keyword': kw,
                        'text': step_text,
                        'status': 'Pending'
                    })
                matched_step = True
                break
        
        # Accumulate Feature Description if no scenario has started yet
        if not matched_step and current_feature and current_scenario is None and not line_stripped.startswith('Feature:'):
            current_feature['description'] += line_stripped + '\n'
                
    return features

def scan_step_implementations(root_dir):
    # Regex to match [Given("...")], [When("...")], [Then("...")], [StepDefinition("...")]
    # Supports both verbatim C# strings [Given(@"...")] and normal strings [Given("...")]
    pattern = re.compile(r'\[(Given|When|Then|StepDefinition)\s*\(\s*@?"([^"]*)"\s*\)\s*\]')
    implemented_patterns = []
    
    for dirpath, _, filenames in os.walk(root_dir):
        if any(ignored in dirpath for ignored in ['.git', '.agents', 'bin', 'obj', 'TestResults']):
            continue
        for filename in filenames:
            if filename.endswith('.cs'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for match in pattern.finditer(content):
                            implemented_patterns.append(match.group(2))
                except Exception:
                    pass
    return implemented_patterns

def is_step_implemented(step_text, implemented_patterns):
    for pat in implemented_patterns:
        try:
            regex_pat = pat
            if not regex_pat.startswith('^'):
                regex_pat = '^' + regex_pat
            if not regex_pat.endswith('$'):
                regex_pat = regex_pat + '$'
            if re.match(regex_pat, step_text):
                return True
        except re.error:
            if pat in step_text:
                return True
    return False

def parse_trx_files(root_dir):
    outcomes = {}
    for dirpath, _, filenames in os.walk(root_dir):
        if any(ignored in dirpath for ignored in ['.git', '.agents', 'bin', 'obj']):
            continue
        for filename in filenames:
            if filename.endswith('.trx'):
                filepath = os.path.join(dirpath, filename)
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    ns = {'ns': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
                    results = root.findall('.//ns:UnitTestResult', ns)
                    for res in results:
                        test_name = res.attrib.get('testName')
                        outcome = res.attrib.get('outcome')
                        if test_name and outcome:
                            base_name = test_name.split('(')[0].strip()
                            normalized_name = base_name.replace('_', ' ').lower()
                            outcomes[normalized_name] = outcome
                except Exception as e:
                    print(f"Error parsing TRX file {filepath}: {e}")
    return outcomes

def parse_junit_files(root_dir):
    outcomes = {}
    for dirpath, _, filenames in os.walk(root_dir):
        if any(ignored in dirpath for ignored in ['.git', '.agents', 'bin', 'obj']):
            continue
        for filename in filenames:
            if filename.endswith('.xml') and not filename.endswith('.trx'):
                filepath = os.path.join(dirpath, filename)
                try:
                    tree = ET.parse(filepath)
                    root = tree.getroot()
                    testcases = root.findall('.//testcase')
                    for tc in testcases:
                        name = tc.attrib.get('name')
                        if name:
                            outcome = 'Passed'
                            if tc.find('failure') is not None:
                                outcome = 'Failed'
                            elif tc.find('error') is not None:
                                outcome = 'Error'
                            elif tc.find('skipped') is not None:
                                outcome = 'Skipped'
                            
                            normalized_name = name.split('(')[0].strip().replace('_', ' ').lower()
                            outcomes[normalized_name] = outcome
                except Exception:
                    pass
    return outcomes

def generate_markdown_report(features, summary):
    timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    md = []
    md.append("# Product Specification & Readiness Report (Living Documentation)")
    md.append("")
    md.append(f"**Compiled on**: {timestamp_str}")
    md.append(f"**Target Scope**: Workspace Scan")
    md.append("")
    md.append("## 📊 Summary Dashboard")
    md.append(f"*   **Total Features**: {summary['total_features']}")
    md.append(f"*   **Feature Readiness**: {summary['feature_readiness_pct']:.2f}%")
    md.append(f"*   **Total Scenarios**: {summary['total_scenarios']}")
    md.append(f"*   **Step Success Rate**: {summary['step_success_rate_pct']:.2f}%")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 📋 Feature Readiness Details")
    md.append("| Feature Link | Scenarios (Passed/Total) | Status | Tags |")
    md.append("| :--- | :--- | :--- | :--- |")
    
    for feat in features:
        rel_path = os.path.relpath(feat['file'])
        passed_scenarios = sum(1 for s in feat['scenarios'] if s['status'] == 'Success')
        total_scenarios = len(feat['scenarios'])
        status = "Ready" if feat['status'] == "Ready" else "In Progress"
        tags_str = ", ".join(f"`{t}`" for t in feat['tags']) if feat['tags'] else "None"
        md.append(f"| [{feat['name']}]({rel_path}) | {passed_scenarios} / {total_scenarios} | {status} | {tags_str} |")
        
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 🔍 Feature Coverage & Requirements Traceability")
    md.append("| User Story ID | Description | Associated Scenarios | Coverage Status |")
    md.append("| :--- | :--- | :--- | :--- |")
    
    stories = {}
    for feat in features:
        story_id = None
        for tag in feat['tags']:
            if re.match(r'^@?(US|STORY|REQ)-\d+$', tag, re.IGNORECASE):
                story_id = tag.upper().replace('@', '')
                break
                
        description_lines = feat['description'].strip().split('\n')
        story_desc = ""
        for line in description_lines:
            if any(term in line.lower() for term in ["as a", "i want to", "so that"]):
                story_desc += line.strip() + " "
                
        if not story_desc:
            story_desc = f"Feature: {feat['name']}"
            
        if not story_id:
            story_id = f"FEAT-{feat['name'].replace(' ', '_').upper()}"
            
        scenarios_list = ", ".join(f"`{s['name']}`" for s in feat['scenarios'])
        coverage_status = "Covered" if len(feat['scenarios']) > 0 else "Gap"
        stories[story_id] = {
            'desc': story_desc.strip(),
            'scenarios': scenarios_list,
            'status': coverage_status
        }
        
    for story_id, info in stories.items():
        md.append(f"| {story_id} | {info['desc']} | {info['scenarios']} | {info['status']} |")
        
    md.append("")
    md.append("---")
    md.append("")
    md.append("## ⚙️ Step-Level Execution Details")
    
    for feat in features:
        md.append("```gherkin")
        md.append(f"Feature: {feat['name']}")
        if feat['description']:
            for line in feat['description'].strip().split('\n'):
                md.append(f"  {line}")
        md.append("")
        
        if feat['background']:
            md.append("  Background:")
            for step in feat['background']:
                md.append(f"    {step['keyword']} {step['text']}")
            md.append("")
            
        for s in feat['scenarios']:
            md.append(f"  Scenario: {s['name']}")
            for step in s['steps']:
                md.append(f"    {step['keyword']} {step['text']} --> [{step['status'].upper()}]")
            md.append("")
        md.append("```")
        md.append("")
        
    return "\n".join(md)

def save_history(features, summary):
    history_dir = os.path.join('.agents', 'bdd', 'history')
    os.makedirs(history_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    run_id = f"run-{timestamp}"
    
    run_data_file = os.path.join(history_dir, f"run-{timestamp}.json")
    run_data = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "summary": summary,
        "features": features
    }
    with open(run_data_file, 'w', encoding='utf-8') as f:
        json.dump(run_data, f, indent=2)
        
    run_report_file = os.path.join(history_dir, f"report-{timestamp}.md")
    report_content = generate_markdown_report(features, summary)
    with open(run_report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    index_file = os.path.join(history_dir, "index.json")
    index_data = []
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except Exception:
            pass
            
    index_entry = {
        "timestamp": datetime.now().isoformat(),
        "run_id": run_id,
        "summary": summary,
        "report_file": run_report_file,
        "data_file": run_data_file
    }
    index_data.insert(0, index_entry)
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)
        
    with open("BDD_REPORT.md", 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"Report saved to BDD_REPORT.md and structured history archived in {history_dir}")

def main():
    root_dir = os.getcwd()
    
    feature_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if any(ignored in dirpath for ignored in ['.git', '.agents', 'bin', 'obj', 'TestResults']):
            continue
        for filename in filenames:
            if filename.endswith('.feature'):
                feature_files.append(os.path.join(dirpath, filename))
                
    all_features = []
    for filepath in feature_files:
        all_features.extend(parse_feature_file(filepath))
        
    if not all_features:
        print("No .feature files found in the project.")
        return
        
    implemented_patterns = scan_step_implementations(root_dir)
    
    trx_outcomes = parse_trx_files(root_dir)
    junit_outcomes = parse_junit_files(root_dir)
    
    test_outcomes = {**junit_outcomes, **trx_outcomes}
    
    total_scenarios = 0
    passed_scenarios = 0
    total_steps = 0
    passed_steps = 0
    
    for feat in all_features:
        feature_ready = True
        
        for step in feat['background']:
            total_steps += 1
            is_impl = is_step_implemented(step['text'], implemented_patterns)
            if is_impl:
                step['status'] = 'Success'
                passed_steps += 1
            else:
                step['status'] = 'Pending'
                
        for s in feat['scenarios']:
            total_scenarios += 1
            
            scen_name_normalized = s['name'].replace('_', ' ').lower()
            outcome = test_outcomes.get(scen_name_normalized)
            
            scen_steps_ready = True
            for step in s['steps']:
                total_steps += 1
                is_impl = is_step_implemented(step['text'], implemented_patterns)
                if is_impl:
                    if outcome in ('Failed', 'FailedTest', 'Fail'):
                        step['status'] = 'Failure'
                    elif outcome in ('Error', 'Timeout'):
                        step['status'] = 'Error'
                    elif outcome == 'Skipped':
                        step['status'] = 'Skipped'
                    else:
                        step['status'] = 'Success'
                        passed_steps += 1
                else:
                    step['status'] = 'Pending'
                    scen_steps_ready = False
                    
            if outcome in ('Failed', 'FailedTest', 'Fail'):
                s['status'] = 'Failure'
                feature_ready = False
            elif outcome in ('Error', 'Timeout'):
                s['status'] = 'Error'
                feature_ready = False
            elif not scen_steps_ready:
                s['status'] = 'Pending'
                feature_ready = False
            else:
                s['status'] = 'Success'
                passed_scenarios += 1
                
        feat['status'] = 'Ready' if feature_ready and len(feat['scenarios']) > 0 else 'In Progress'
        
    ready_features = sum(1 for f in all_features if f['status'] == 'Ready')
    
    summary = {
        "total_features": len(all_features),
        "ready_features": ready_features,
        "feature_readiness_pct": (ready_features / len(all_features) * 100) if all_features else 0,
        "total_scenarios": total_scenarios,
        "passed_scenarios": passed_scenarios,
        "step_success_rate_pct": (passed_steps / total_steps * 100) if total_steps else 0
    }
    
    save_history(all_features, summary)

if __name__ == '__main__':
    main()
