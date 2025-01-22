from flask import Flask, request, jsonify, render_template
from difflib import SequenceMatcher

app = Flask(__name__)

# Helper functions
def closest_match(word, dictionary, threshold=0.8):
    max_ratio, best_match = 0, None
    for dict_word in dictionary:
        ratio = SequenceMatcher(None, word, dict_word).ratio()
        if ratio > max_ratio:
            max_ratio, best_match = ratio, dict_word
    return best_match if max_ratio >= threshold else None

def indian_numeric_to_number(s, threshold=0.5):
    indian_numeric_system = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
        'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
        'hundred': None, 'thousand': None, 'lakh': None, 'crore': None,
        'only': 0, 'and': 0
    }
    words = s.lower().split()
    result, temp = 0, 0
    corrected_words = []

    for word in words:
        if word in indian_numeric_system:
            corrected_words.append(word)
        else:
            correction = closest_match(word, indian_numeric_system, threshold)
            if correction:
                corrected_words.append(correction)
            else:
                # Exclude unmatchable words
                corrected_words.append(f"[{word}]")  # Mark as uncorrected for debugging

    for word in corrected_words:
        if word in indian_numeric_system:
            if word == 'hundred':
                temp *= 100
            elif word == 'thousand':
                result += temp * 1000
                temp = 0
            elif word == 'lakh':
                result += temp * 100000
                temp = 0
            elif word == 'crore':
                result += temp * 10000000
                temp = 0
            else:
                temp += indian_numeric_system[word]

    return result + temp, ' '.join(corrected_words)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        words = request.form.get('amount_in_words')
        if not words:
            return jsonify({'error': 'Please enter an amount in words.'}), 400

        number, corrected_words = indian_numeric_to_number(words)
        return jsonify({'success': True, 'number': number, 'corrected_words': corrected_words})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
