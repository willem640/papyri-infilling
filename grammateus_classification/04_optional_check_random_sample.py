from textual.app import App
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, Middle, Right, Center, Vertical, VerticalGroup
from textual.content import Content
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, Link, Placeholder, Static

import json
import random
import re


class PapyrusViewer(Vertical):
    DEFAULT_CSS = """
    .neutral-border {
        border: heavy white;
    }
    .incorrect-border {
        border: heavy red;
    }
    .correct-border {
        border: heavy green;
    }
    """
    grammateus_types = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]

    current_papyrus_idx = reactive(0, recompose=True)
    
    checked_papyri = []

    def compose(self):
        with HorizontalGroup(classes=self.get_header_class()):
            yield Label(self.current_papyrus['id'])
            with Center():
                yield Label(self.get_marked_as())
            with Right():
                yield Label(f"Progress: {self.current_papyrus_idx}/{len(self.papyri_with_classes)+1}")
        # with Vertical(classes='neutral-border'):
        with Vertical(classes='neutral-border'):
            yield Label(f"[b]Model guess:[/b]\n{self.current_papyrus['grammateus_type']}\n")
            yield Label(f"[b]HGV text classes:[/b]\n{', '.join(self.current_papyrus['text_classes'])}")
            yield Link(f"{self.get_url_for(self.current_papyrus['id'])}")
            yield Label(f"\n[b]Text edition:[/b]\n" + self.current_papyrus['training_text'])

        #yield Placeholder()
       
    def get_marked_as(self):
        current_correct = self.is_current_correct()

        if current_correct is None:
            return 'Has not been checked'
        elif current_correct:
            return 'Marked correct'
        elif not current_correct:
            return 'Marked incorrect'
        else:
            return "Error checking correct/incorred"

    def get_url_for(self, papyrus_id: str):
        if ddbdp_id := re.search(r'DDbDP\/([\w\d.]+)\/', papyrus_id):
            # I want to replace backwards:
            # p.mich.5.326 -> p.mich;5;326
            # so reverse string, do replace with limit, reverse again
            ddbdp_id_subbed = ddbdp_id.group(1)[::-1].replace('.', ';', 2)[::-1]
            papyri_info_link = f"https://papyri.info/ddbdp/{ddbdp_id_subbed}"
            return papyri_info_link
    def get_header_class(self):
        current_correct = self.is_current_correct()

        if current_correct is None:
            return 'neutral-border'
        elif current_correct:
            return 'correct-border'
        elif not current_correct:
            return 'incorrect-border'

    def is_current_correct(self):
        found_in_corrected = None
        for checked in self.checked_papyri:
            if checked['id'] == self.current_papyrus['id']:
                found_in_corrected = checked['correct']
        
        return found_in_corrected


    def __init__(self):
        super().__init__()
        with open('./papyri_with_classes.json') as f:
            self.papyri_with_classes = json.load(f)
            random.Random(42).shuffle(self.papyri_with_classes)

        try: 
            with open('./checked_papyri.json') as f:
                self.checked_papyri = json.load(f)
        except FileNotFoundError:
            self.checked_papyri = []

    @property
    def current_papyrus(self):
        return self.papyri_with_classes[self.current_papyrus_idx]
    
    def prev_papyrus(self):
        if self.current_papyrus_idx > 0:
            self.current_papyrus_idx -= 1
            # TODO maybe a message if the last one has been reached?

    def next_papyrus(self):
        if self.current_papyrus_idx + 1 < len(self.papyri_with_classes):
            self.current_papyrus_idx += 1

    def mark_current_correct(self):
        was_already_checked = False
        for i in range(len(self.checked_papyri)):
            papyrus = self.checked_papyri[i]
            if papyrus['id'] == self.current_papyrus['id']:
                self.checked_papyri[i]['correct'] = True
                was_already_checked = True
                break
        if not was_already_checked:
            self.checked_papyri.append({'correct': True, **self.papyri_with_classes[self.current_papyrus_idx]})
        self.refresh(recompose=True)

    def mark_current_incorrect(self):
        was_already_checked = False
        for i in range(len(self.checked_papyri)):
            papyrus = self.checked_papyri[i]
            if papyrus['id'] == self.current_papyrus['id']:
                self.checked_papyri[i]['correct'] = False
                was_already_checked = True
                break
        if not was_already_checked:
            self.checked_papyri.append({'correct': False, **self.papyri_with_classes[self.current_papyrus_idx]})
        self.refresh(recompose=True)


class PapyriCheckerApp(App):
   
    BINDINGS = [('right', 'next_papyrus', 'Go to next papyrus (skip)'), 
                ('left', 'prev_papyrus', 'Go to previous papyrus'),
                ('c', 'mark_current_correct', 'Mark current papyrus as correct'),
                ('i', 'mark_current_incorrect', 'Mark current papyrus as incorrect'),
                ('C', 'mark_current_correct_and_next', 'Mark current papyrus as correct and move to next'),
                ('I', 'mark_current_incorrect_and_next', 'Mark current papyrus as incorrect and move to next')
                ]


    def compose(self):
        yield Header()
        yield PapyrusViewer()
        yield Footer()


    def action_prev_papyrus(self):
        self.query_one(PapyrusViewer).prev_papyrus()

    def action_next_papyrus(self):
        self.query_one(PapyrusViewer).next_papyrus()

    def action_mark_current_correct(self):
        self.query_one(PapyrusViewer).mark_current_correct()

    def action_mark_current_incorrect(self):
        self.query_one(PapyrusViewer).mark_current_incorrect()

    def action_mark_current_correct_and_next(self):
        self.query_one(PapyrusViewer).mark_current_correct()
        self.action_next_papyrus()

    def action_mark_current_incorrect_and_next(self):
        self.query_one(PapyrusViewer).mark_current_incorrect()
        self.action_next_papyrus()


   

if __name__=="__main__":
    types = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]
    with open('./papyri_with_classes.json') as f:
        papyri_with_classes = json.load(f)
    
    app = PapyriCheckerApp()
    app.run()
