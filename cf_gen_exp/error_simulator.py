import random
import spacy
from lemminflect import getInflection
# import nlpaug.augmenter.char as nac
import nlpaug.augmenter.word as naw
import numpy as np


class ErrorSimulator:

    def __init__(self, nlp, error_rate=0.5, seed=42):
        self.error_rate = error_rate
        self.nlp = nlp
        random.seed(seed)
        np.random.seed(seed)

    def introduce_errors(self,
                         text,
                         intervention_level='in_sentence',
                         in_sent_mode='spelling',
                         in_sent_aug_p=0.3):
        if intervention_level == 'paragraph':
            return self.paragraph_level_intervention(text)
        elif intervention_level == 'discourse':
            return self.discourse_level_intervention(text)
        elif intervention_level == 'in_sentence':
            return self.in_sentence_intervention(text, in_sent_mode,
                                                 in_sent_aug_p)
        else:
            raise ValueError(
                f"Unknown intervention level: {intervention_level}")

    def in_sentence_intervention(self, text, mode, aug_p):

        # print(text)

        sentences = list(self.nlp(text).sents)
        num_sentences = len(sentences)

        num_sentences_to_modify = max(1,
                                      round(num_sentences * self.error_rate))
        indices_to_modify = sorted(
            random.sample(range(num_sentences), num_sentences_to_modify))

        processed_sentences = [
            self._process_sentence(sentence, mode, aug_p)
            if index in indices_to_modify else sentence.text
            for index, sentence in enumerate(sentences)
        ]
        return ' '.join(processed_sentences)

    def _process_sentence(self, sentence, mode, aug_p):
        # Check if the sentence ends with one or two newline characters
        ends_with_newline = sentence.text.endswith('\n')
        ends_with_double_newline = sentence.text.endswith('\n\n')

        # Remove the newline characters for processing
        sentence_text = sentence.text.rstrip('\n')

        if mode == 'spelling':
            aug = naw.SpellingAug(aug_p=aug_p)
        elif mode == 'word_order':
            aug = naw.RandomWordAug(action="swap", aug_p=aug_p)
        elif mode == 'sva':
            aug = SVADisruptor(self.nlp)
        else:
            raise ValueError(f"Unknown error mode: {mode}")

        augmented_texts = aug.augment(sentence_text)

        # if len(augmented_texts) < 1:
        #     print(sentence.text)

        # print(sentence.text)
        # print('-' * 20)

        # 检查 augmented_texts 是否为空列表、空字符串，或完全由空白字符构成
        if not augmented_texts or (isinstance(augmented_texts, str)
                                   and augmented_texts.isspace()):
            augmented_text = ''
        elif isinstance(augmented_texts, list):
            augmented_text = augmented_texts[0]
        else:
            augmented_text = augmented_texts

        # Restore the newline characters
        if ends_with_double_newline:
            return augmented_text + '\n\n'
        elif ends_with_newline:
            return augmented_text + '\n'
        else:
            return augmented_text

    def paragraph_level_intervention(self, text):
        paragraphs = text.split('\n\n')
        processed_paragraphs = [
            self.rearrange_within_paragraph(para) for para in paragraphs
        ]
        return '\n\n'.join(processed_paragraphs)

    def discourse_level_intervention(self, text):
        # Step 1: Index sentences and determine their ending newlines
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        sentence_endings = [('' if not sent.text.endswith('\n') else
                             '\n\n' if sent.text.endswith('\n\n') else '\n')
                            for sent in doc.sents]

        # Step 2: Perform sentence swapping
        num_sentences_to_swap = max(1, round(len(sentences) * self.error_rate))
        indices_to_swap = sorted(
            random.sample(range(len(sentences)), num_sentences_to_swap))
        swapped_sentences = self.perform_sentence_swapping(
            sentences, indices_to_swap)

        # Step 3: Reconstruct paragraphs while preserving single and double newlines
        reconstructed_paragraphs = []
        current_paragraph = []

        for sentence, ending in zip(swapped_sentences, sentence_endings):
            # Strip existing newlines and add the appropriate ending
            current_paragraph.append(sentence.rstrip('\n') + ending)
            if ending == '\n\n':
                reconstructed_paragraphs.append(''.join(current_paragraph))
                current_paragraph = []

        # Add the last paragraph if any
        if current_paragraph:
            reconstructed_paragraphs.append(''.join(current_paragraph))

        return ''.join(reconstructed_paragraphs)

    # def discourse_level_intervention(self, text):
    #     paragraphs = text.split('\n\n')
    #     all_sentences = []
    #     for para in paragraphs:
    #         sentences = [sent.text for sent in self.nlp(para).sents]
    #         # Mark the last sentence of a paragraph to preserve paragraph structure
    #         if sentences:
    #             sentences[-1] += '\n\n'
    #         else:
    #             sentences.append('\n\n')
    #         all_sentences.extend(sentences)

    #     num_sentences = len(all_sentences)
    #     num_sentences_to_swap = max(1, round(num_sentences * self.error_rate))

    #     indices_to_swap = sorted(random.sample(range(num_sentences), num_sentences_to_swap))
    #     new_order_sentences = self.perform_sentence_swapping(all_sentences, indices_to_swap)

    #     # Join sentences to form the reconstructed text
    #     reconstructed_text = ''.join(new_order_sentences).strip()

    #     return reconstructed_text

    # def discourse_level_intervention(self, text):
    #     """This version ignore newlines."""
    #     paragraphs = text.split('\n\n')
    #     all_sentences = [sent for para in paragraphs for sent in self.nlp(para).sents]
    #     num_sentences = len(all_sentences)
    #     num_sentences_to_swap = max(1, round(num_sentences * self.error_rate))

    #     # Randomly select indices for sentences to be swapped
    #     indices_to_swap = sorted(random.sample(range(num_sentences), num_sentences_to_swap))

    #     # Perform the swapping
    #     new_order_sentences = self.perform_sentence_swapping(all_sentences, indices_to_swap)
    #     return ' '.join(new_order_sentences)

    def perform_sentence_swapping(self, sentences, indices_to_swap):
        new_order_sentences = sentences.copy(
        )  # Create a copy to preserve original order
        shuffled_indices = np.random.permutation(indices_to_swap)

        # Map original indices to shuffled indices
        for original, new in zip(indices_to_swap, shuffled_indices):
            new_order_sentences[new] = sentences[original]

        return new_order_sentences

    def rearrange_within_paragraph(self, paragraph):
        sentences = list(self.nlp(paragraph).sents)
        indices = range(len(sentences))
        shuffled_indices = np.random.permutation(indices)
        return ' '.join([sentences[i].text for i in shuffled_indices])


class SVADisruptor:

    def __init__(self, nlp):
        self.nlp = nlp

    def find_subject(self, verb):
        # 查找所有可能的主语，包括复合主语
        subjects = [
            child for child in verb.children
            if child.dep_ in ['nsubj', 'nsubjpass']
        ]

        # 如果动词的依存关系是 'relcl'，则它修饰的名词是主语
        if verb.dep_ == 'relcl' and verb.head.pos_ in ['NOUN', 'PROPN']:
            # 检查是否有关系代词指向主语
            rel_pronoun = [
                child for child in verb.children
                if child.dep_ == 'nsubj' and child.head.dep_ == 'relcl'
            ]
            # 如果有，主语应该是这个动词的头部（它修饰的名词）
            if rel_pronoun:
                subjects = [verb.head]  # 用它修饰的名词代替定语从句中的关系代词
            else:
                # 否则，可能是诸如 "The books that are on the table" 这样的情况，其中 "that" 是主语
                subjects.extend(rel_pronoun)
        else:
            # 如果主语是由 'and' 连接的复合主语，我们添加所有 'conj' 连接的主语
            for subject in subjects:
                subjects.extend(child for child in subject.children
                                if child.dep_ == 'conj')

        return subjects

    def find_auxiliary(self, verb):
        # 寻找与给定动词相关的助动词
        for possible_aux in verb.children:
            if possible_aux.dep_ in ['aux', 'auxpass']:
                return possible_aux
        return None

    def identify_verb_tense_and_person(self, verb, subjects=[]):
        tense = 'none'
        person = 'none'

        # 确定时态
        if verb.tag_ in ['VBD', 'VBN']:  # 过去时
            tense = 'past'
        elif verb.tag_ in ['VBG', 'VBZ', 'VBP', 'VB']:  # 现在时或原形
            tense = 'present'
        elif verb.tag_ == 'MD':  # 情态动词，可能表示将来时
            tense = 'future'

        # 确定人称和数
        if len(subjects) > 1:
            # 如果主语是复合主语，则不是第三人称
            person = 'non-third'
        elif len(subjects) == 1:
            subject = subjects[0]
            # 如果主语是代词，直接判断人称
            if subject.tag_ == 'PRP':
                if subject.lower_ in ['i', 'we', 'you', 'they']:
                    person = 'non-third'
                elif subject.lower_ in ['he', 'she', 'it']:
                    person = 'third'
            # 如果主语是名词，根据单复数形式判断
            else:
                if subject.tag_ in ['NN', 'NNP']:  # 单数名词
                    person = 'third'
                elif subject.tag_ in ['NNS', 'NNPS']:  # 复数名词
                    person = 'non-third'
        else:
            if verb.tag_ == 'VBZ':  # Third person singular present
                person = 'third'
            elif verb.tag_ == 'VBP':  # Non-third person singular present
                person = 'non-third'

        return tense, person

    def augment(self, sentence):
        doc = self.nlp(sentence)
        replacements = []

        for token in doc:

            if token.dep_ in [
                    'ROOT', 'relcl', 'ccomp', 'xcomp', 'acl', 'advcl'
            ]:
                subjects = self.find_subject(token)
                auxiliary = self.find_auxiliary(token)
                # print(token.head)

                tense, person = self.identify_verb_tense_and_person(
                    auxiliary if auxiliary else token, subjects)

                if tense == 'past':
                    if auxiliary and auxiliary.lower_ in ['was', 'were']:
                        disrupt_form = 'were' if person == 'third' else 'was'
                        replacements.append(
                            (auxiliary.idx, auxiliary.idx + len(auxiliary),
                             disrupt_form))
                    elif token.text.lower() in ['was', 'were']:
                        disrupt_form = 'were' if person == 'third' else 'was'
                        replacements.append(
                            (token.idx, token.idx + len(token), disrupt_form))

                elif tense == 'present':

                    if person == 'third':
                        possible_inflections = getInflection(
                            auxiliary.lemma_ if auxiliary else token.lemma_,
                            'VBP')
                    else:
                        possible_inflections = getInflection(
                            auxiliary.lemma_ if auxiliary else token.lemma_,
                            'VBZ')

                    if len(possible_inflections) == 0:
                        continue

                    disrupt_form = possible_inflections[-1]
                    replacements.append(
                        (auxiliary.idx if auxiliary else token.idx,
                         auxiliary.idx +
                         len(auxiliary) if auxiliary else token.idx +
                         len(token), disrupt_form))

        # 应用替换
        for start, end, replacement in reversed(replacements):
            sentence = sentence[:start] + replacement + sentence[end:]

        return sentence


# Example usage
if __name__ == "__main__":

    # initializing spacy model
    nlp = spacy.load("en_core_web_sm")

    # # sample_text = "The quick brown fox jumps over the lazy dog. It was a sunny day."
    # sample_text = '''The quick brown fox jumps over the lazy dog.\n This sentence, known for containing every letter of the alphabet, is often used in typing practice. It is recognized worldwide.\n\nHowever, did you know that other sentences, like "Pack my box with five dozen liquor jugs," also contain every letter? These types of sentences are known as pangrams. Pangrams are used in font displays, calligraphy, and typing skills development.\n\nInterestingly, pangrams exist in many languages.\n For example, the Spanish sentence "Benjamín pidió una bebida de kiwi y fresa; Noé, sin vergüenza, la más exquisita champaña del menú." is a well-known example. Each language has its own unique pangrams, which often reflect cultural aspects or common phrases.'''

    # error_simulator = ErrorSimulator(nlp, error_rate=0.5, seed=42)
    # print(
    #     error_simulator.introduce_errors(sample_text,
    #                                      intervention_level="discourse",
    #                                      in_sent_mode="word_order")
    # )  # This will show the text with simulated errors

    disruptor = SVADisruptor(nlp)
    # sentence = "The cat and the dog find the birds in the garden."
    # print("Original:", sentence)
    # print("Disrupted:", disruptor.augment(sentence))

    # sentence = "There are many reasons for the success of the project."
    # print("Original:", sentence)
    # print("Disrupted:", disruptor.augment(sentence))
    
    # sentence = "The team is wearing their new jerseys."
    # sentence = "The audience are silent during the performance."
    # sentence = "My family loves to spend time at the beach."
    sentence = "Neither the dogs nor the cat run in the yard."
    print("Original:", sentence)
    print("Disrupted:", disruptor.augment(sentence))
