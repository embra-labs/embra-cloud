// Shared behaviour for /engineering/ posts: language label and copy button on code blocks.
document.querySelectorAll('article pre').forEach(function (pre) {
  var code = pre.querySelector('code');
  var wrap = document.createElement('div');
  wrap.className = 'code-wrap';
  pre.parentNode.insertBefore(wrap, pre);
  wrap.appendChild(pre);
  var m = code && /language-([\w-]+)/.exec(code.className);
  if (m && m[1] !== 'none') {
    var label = document.createElement('span');
    label.className = 'code-lang';
    label.textContent = m[1];
    wrap.appendChild(label);
  }
  if (!navigator.clipboard) return;
  var btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'code-copy';
  btn.textContent = 'Chép';
  btn.addEventListener('click', function () {
    navigator.clipboard.writeText((code || pre).innerText).then(function () {
      btn.textContent = 'Đã chép';
      setTimeout(function () { btn.textContent = 'Chép'; }, 1500);
    });
  });
  wrap.appendChild(btn);
});
