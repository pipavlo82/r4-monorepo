document.getElementById('generateBtn').addEventListener('click', function() {
    // Генерація 1000 чисел
    const array = new Uint32Array(1000);
    window.crypto.getRandomValues(array);
    const randomNumbers = Array.from(array).map(val => val % 100);

    // Вивід перших 10 чисел
    const output = document.getElementById('output');
    output.innerHTML = `
        <p>Перші 10 чисел (0-99): ${randomNumbers.slice(0, 10).join(', ')}</p>
    `;

    // Анімована гістограма
    const canvas = document.getElementById('histogram');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const bins = new Array(10).fill(0);
    randomNumbers.forEach(num => bins[Math.floor(num / 10)]++);

    const maxBin = Math.max(...bins);
    const barWidth = canvas.width / bins.length;
    let animationProgress = 0;

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00ffcc';
        ctx.strokeStyle = '#ffffff';
        ctx.font = '12px Arial';

        bins.forEach((count, i) => {
            const barHeight = (count / maxBin) * (canvas.height - 30) * animationProgress;
            ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 4, barHeight);
            ctx.fillStyle = 'white';
            ctx.fillText(`${i*10}-${i*10+9}`, i * barWidth + 5, canvas.height - 10);
            ctx.fillStyle = '#00ffcc';
        });

        animationProgress += 0.05;
        if (animationProgress < 1) {
            requestAnimationFrame(animate);
        }
    }
    animate();
});
