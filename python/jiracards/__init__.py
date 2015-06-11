from reportlab.lib.colors import red, black
import re

ISSUE_TYPE2COLOR = {
    'task': black,
    'bug': red
}

JIRA_KEY_REGEXP = re.compile(r'^[A-Z][A-Z0-9]+-[1-9][0-9]*$')

EPIC_COLORS = {
    'ghx-label-1': '#815b3a',
    'ghx-label-2': '#f79232',
    'ghx-label-3': '#d39c3f',
    'ghx-label-4': '#3b7fc4',
    'ghx-label-5': '#4a6785',
    'ghx-label-6': '#8eb021',
    'ghx-label-7': '#ac707a',
    'ghx-label-8': '#654982',
    'ghx-label-9': '#f15c75'
}
