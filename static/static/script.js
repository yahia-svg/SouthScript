document.addEventListener('DOMContentLoaded', function() {
    const pages = document.querySelectorAll('.page');
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(target).classList.add('active');
            
            navLinks.forEach(link => link.classList.remove('active'));
            this.classList.add('active');
            
            if (target === 'playground' && !window.termInitialized) {
                initTerminal();
                window.termInitialized = true;
            }
        });
    });
    
    if (window.location.hash === '#playground' || 
        (window.location.hash === '' && document.querySelector('.page.active').id === 'playground')) {
        initTerminal();
        window.termInitialized = true;
    }
});

function initTerminal() {
    const term = new Terminal({
        cursorBlink: true,
        fontFamily: 'Roboto Mono, monospace',
        theme: {
            background: '#2a2a2a',
            foreground: '#f8f8f8',
            cursor: '#ff7b25',
            selection: 'rgba(255,123,37,0.3)'
        },
        allowTransparency: true,
        scrollback: 1000,

        cols: 80, 
        rows: 24   
    });

    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    
    const terminalElement = document.getElementById('terminal');
    term.open(terminalElement);
    

    setTimeout(() => {
        fitAddon.fit();

        const core = term._core;
        if (core._renderService.dimensions.actualCellHeight > 0) {
            const rows = Math.floor(terminalElement.offsetHeight / 
                                core._renderService.dimensions.actualCellHeight);
            term.resize(term.cols, rows - 1); 
        }
    }, 50);


    let currentInput = '';

    term.write('$ ');

    term.onData(data => {
        if (data === '\r') {
            executeCode(term, currentInput);
            currentInput = '';
        } else if (data === '\x7F') {
            if (currentInput.length > 0) {
                currentInput = currentInput.slice(0, -1);
                term.write('\b \b');
            }
        } else {
            currentInput += data;
            term.write(data);
        }
    });

    window.addEventListener('resize', () => fitAddon.fit());
}

async function executeCode(term, code) {
    term.write('\r\n');
    
    try {
        const response = await fetch('/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        
        const result = await response.json();
        const lines = result.output.split('\n');
        
        if (result.isError) {
            term.write('\x1b[31m');
        }
        
        lines.forEach(line => {
            if (line.trim().length > 0) {
                term.writeln(line.trim());
            }
        });
        
        if (result.isError) {
            term.write('\x1b[0m');
        }
        
    } catch (err) {
        term.write('\x1b[31m');
        term.writeln('File <web>, line 1');
        term.writeln(`Network Error: ${err.message}`.trim());
        term.write('\x1b[0m');
    }
    
    term.write('$ ');
}