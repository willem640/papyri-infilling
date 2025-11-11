from typing import List
from textual import work
from textual.app import App
from textual.containers import Horizontal, HorizontalGroup, HorizontalScroll, Middle, Right, Center, Vertical, VerticalGroup
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Label, Link, ListItem, ListView

import json
import random
import re

GRAMMATEUS_TYPES = ["Epistolary Exchange", "Objective Statement", "Recording of Information", "Transmission of Information"]

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
    .manual-border {
        border: heavy purple;
    }
    Label {
        text-wrap: wrap;
    }
    """

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
            if self.is_current_manual():
                yield Label(f"[b]Manual label:[/b]\n{self.find_current_in_corrected()['grammateus_type']}\n")
            yield Label(f"[b]HGV title:[/b]\n{self.current_papyrus['hgv_title']}\n")
            yield Label(f"[b]HGV text classes:[/b]\n{', '.join(self.current_papyrus['text_classes'])}")
            yield Link(f"{self.get_url_for(self.current_papyrus['id'])}")
            yield Label(f"\n[b]Text edition:[/b]\n" + self.current_papyrus['training_text'])

        #yield Placeholder()


    def get_marked_as(self):
        current_correct = self.get_current_correction()

        if current_correct is None:
            return 'Has not been checked'
        elif current_correct is True:
            return 'Marked correct'
        elif current_correct is False:
            return 'Marked incorrect'
        elif current_correct == 'manual':
            return 'Manually set'
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
        current_correct = self.get_current_correction()

        if current_correct is None:
            return 'neutral-border'
        elif current_correct is True:
            return 'correct-border'
        elif current_correct is False:
            return 'incorrect-border'
        elif current_correct == 'manual':
            return 'manual-border'
        else:
            return 'neutral-border'

    def find_current_in_corrected(self):
        found_in_corrected = None
        for checked in self.checked_papyri:
            if checked['id'] == self.current_papyrus['id']:
                found_in_corrected = checked        

        return found_in_corrected


    def get_current_correction(self):
        found = self.find_current_in_corrected()

        if found is None:
            return None

        return found['correct']

    def is_current_manual(self):
        found = self.find_current_in_corrected()

        if found is None or found.get('manually_set') is None:
            return False

        return True

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
        self.set_interval(10, self.save)

    def save(self):
        print("Saving...")
        with open('./checked_papyri.json', 'w') as f:
            json.dump(self.checked_papyri, f)
        print("Saved checked papyri")


    def on_unmount(self,_):
        self.save()

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


    def set_on_checked(self, key, value):
        was_already_checked = False
        for i in range(len(self.checked_papyri)):
            papyrus = self.checked_papyri[i]
            if papyrus['id'] == self.current_papyrus['id']:
                self.checked_papyri[i][key] = value
                was_already_checked = True
                break
        if not was_already_checked:
            self.checked_papyri.append({**self.papyri_with_classes[self.current_papyrus_idx], key: value})
        self.refresh(recompose=True)


    def mark_current_correct(self):
        self.set_on_checked('correct', True)

    def mark_current_incorrect(self):
        self.set_on_checked('correct', False)


    def set_type(self, new_type):
        self.set_on_checked('correct', 'manual')
        self.set_on_checked('manually_set', True) # correct may be overwritten, this may not
        self.set_on_checked('grammateus_type', new_type)

class ChoosePapyrusTypeModal(ModalScreen[str | None]):
    DEFAULT_CSS = """
        ChoosePapyrusTypeModal {
            align: center middle;
        }

        ListView {
            width: 30;
            height: auto;
            margin: 2 2;
        }

        Label {
            padding: 1 2;
        }
    """
    BINDINGS = [
            ('escape', 'cancel', 'Cancel (don\'t select anything)')
    ]

    def __init__(self, types: List[str]):
        super().__init__()
        self.types = types

    def compose(self):
        yield Label("Choose the correct text class:")
        yield ListView() # Children will be set in on_mount

    def on_mount(self):
        for this_type in self.types:
            self.query_one(ListView)\
                .append(ListItem(
                    Label(this_type)
                    )
                )

    def on_key(self, event) -> None:
        numbers = [str(i + 1) for i in range(9)]

        if event.key in numbers:
            index = int(event.key) - 1
            self.dismiss(self.types[index])
        

    def on_list_view_selected(self, message):
        self.dismiss(self.types[message.index])
        
    def action_cancel(self):
        self.dismiss(None)

class PapyriCheckerApp(App):
   
    BINDINGS = [('right,n', 'next_papyrus', 'Go to next papyrus (skip)'), 
                ('left,N', 'prev_papyrus', 'Go to previous papyrus'),
                ('C', 'mark_current_correct', 'Mark current papyrus as correct'),
                ('I', 'mark_current_incorrect', 'Mark current papyrus as incorrect'),
                ('c', 'mark_current_correct_and_next', 'Mark current papyrus as correct and move to next'),
                ('i', 'mark_current_incorrect_and_next', 'Mark current papyrus as incorrect and move to next'),
                ('a', 'papyrus_category_modal', 'Assign category to current papyrus'),
                ('1', 'mark_as_epistolary', 'Mark as Epistolary Exchange and move to next'),
                ('2', 'mark_as_objective', 'Mark as Objective Statement and move to next'),
                ('3', 'mark_as_recording', 'Mark as Recording of Information and move to next'),
                ('4', 'mark_as_transmission', 'Mark as Transmission of Information and move to next'),
                ]


    def compose(self):
        yield Header()
        yield PapyrusViewer()
        yield Footer()

    async def action_papyrus_category_modal(self):
        def modal_close(new_cat):
            if new_cat is not None:
                self.query_one(PapyrusViewer).set_type(new_cat)
        self.push_screen(ChoosePapyrusTypeModal(GRAMMATEUS_TYPES), modal_close)

    def action_mark_as_epistolary(self):
        self.query_one(PapyrusViewer).set_type(GRAMMATEUS_TYPES[0])
        self.action_next_papyrus()

    def action_mark_as_objective(self):
        self.query_one(PapyrusViewer).set_type(GRAMMATEUS_TYPES[1])
        self.action_next_papyrus()

    def action_mark_as_recording(self):
        self.query_one(PapyrusViewer).set_type(GRAMMATEUS_TYPES[2])
        self.action_next_papyrus()

    def action_mark_as_transmission(self):
        self.query_one(PapyrusViewer).set_type(GRAMMATEUS_TYPES[3])
        self.action_next_papyrus()

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
    with open('./papyri_with_classes.json') as f:
        papyri_with_classes = json.load(f)
    
    app = PapyriCheckerApp()
    app.run()
