

import csv
import os
from collections import defaultdict

def load_tree(tsv_path):
    nodes = {}
    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            nodes[row['id']] = row
    return nodes

def get_dominant_signal(signals, axis):
    axis_signals = {}
    for key, count in signals.items():
        if key.startswith(axis + ':'):
            value = key.split(':')[1]
            axis_signals[value] = axis_signals.get(value, 0) + count
    if not axis_signals:
        return "neutral"
    return max(axis_signals, key=axis_signals.get)

def run_tree():
    # Find the TSV file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tsv_path = os.path.join(script_dir, '..', 'tree', 'reflection-tree.tsv')
    nodes = load_tree(tsv_path)
    
    state = {
        'answers': {},
        'signals': defaultdict(int)
    }
    
    current = 'START'
    
    while current and current in nodes:
        node = nodes[current]
        n_type = node['type']
        text = node['text']
        
        # Replace {A0_OPEN.answer} with actual answers
        for k, v in state['answers'].items():
            text = text.replace(f"{{{k}.answer}}", v)
        
        # Replace {axis1.dominant} with tally results
        for axis in ['axis1', 'axis2', 'axis3']:
            dom = get_dominant_signal(state['signals'], axis)
            text = text.replace(f"{{{axis}.dominant}}", dom)
        
        if n_type == 'start':
            print(text)
            current = 'A0_OPEN'
            
        elif n_type == 'question':
            print(f"\n{text}")
            opts = node['options'].split('|')
            for i, opt in enumerate(opts, 1):
                print(f" {i}) {opt}")
            while True:
                try:
                    choice = int(input("Choose: ")) - 1
                    if 0 <= choice < len(opts):
                        break
                    else:
                        print("Invalid number. Try again.")
                except ValueError:
                    print("Enter a number. Try again.")
            state['answers'][node['id']] = opts[choice]
            current = node['target']
            
        elif n_type == 'decision':
            parent_answer = state['answers'][node['parentId']]
            for rule in node['options'].split(','):
                cond, next_id = rule.split(':')
                valid_answers = cond.replace('answer=', '').split('|')
                if parent_answer in valid_answers:
                    current = next_id
                    break
                    
        elif n_type in ['reflection', 'bridge']:
            print(f"\n{text}")
            if node['signal']:
                state['signals'][node['signal']] += 1
            current = node['target']
            
        elif n_type == 'summary':
            print(f"\n{text}")
            current = 'END'
            
        elif n_type == 'end':
            print(f"\n{text}")
            current = None

if __name__ == "__main__":
    run_tree()
