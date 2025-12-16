# WebNovelScrapper
A Web Novel Downloader for syosetu.com and kakuyomu.jp
Creates HTML files for the novels that can be imported to Calibre to create ebooks.
Just go to the page on those website and copy the code for the book from the address bar.
I only tested this script on Windows.

Run the script with Python and supply the code as an argument.
E.g. run "python main.py >code<" from the command line.

Other options, such as the output folder will be asked for by the script if they haven't been given via other optional arguments.
Those settings can also be saved and everything can be run faster later on with the "-f" option.

Options include (for the moment):

-c >number< : Chapters flag, sets the size of a single book in number of chapters. Default value is -1, i.e. all chapters in a single file.

-f : Fast flag, don't ask for different settings if they have been saved before. Use this to get the script going faster.

-o >path< : Output flag, the output file(s) will be created at the given path.

-q : Quiet flag, don't print so much on the console.

-r >start<:>finish< : Range flag, only downloads a portion of the book. The numbers start and finish have to be seperated by a collon. 
                      No value for start or finish is also acceptible and will be interpreted as first and last chapter respectively.

-s [syosetu|kakuyomu] : Site flag, tries to download the book from this website. Without this flag the right website will be choosen automatically from the code.
