# vhs demo tape for proxy-checker
# Run: vhs demo.tape → produces demo.gif

Output demo.gif

Set Shell "zsh"
Set FontSize 15
Set Width 1100
Set Height 640
Set Theme "Dracula"
Set TypingSpeed 35ms
Set PlaybackSpeed 1.0
Set Padding 20

Hide
Type "export PATH=$HOME/.local/bin:$PATH"
Enter
Type "setopt INTERACTIVE_COMMENTS"
Enter
Type "export PS1='%F{cyan}~/proxy-checker%f $ '"
Enter
Type "clear"
Enter
Show

Sleep 700ms
Type "# fetch 30 free HTTP proxies and validate them"
Enter
Sleep 500ms
Type "proxy-checker fetch --count 30 --type http"
Sleep 400ms
Enter

# Real run takes ~11s
Sleep 13s

Type "# alive proxies saved. ship it."
Enter
Sleep 2000ms
