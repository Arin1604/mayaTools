import argparse
import re
import os
import shutil



def main():
    parser = argparse.ArgumentParser(description="This is a simple batch renaming tool to rename sequences of files",
                                     usage="To replace all files with hello wtih goodbye: python clirenamer.py hello goodbye")

    parser.add_argument('instring', help="The word to replace")
    

    args = parser.parse_args()
if __name__ == '__main__':
    main()