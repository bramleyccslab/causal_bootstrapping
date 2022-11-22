
const combos = [
  [1, 'construct'],
  [1, 'combine'],
  [1, 'decon'],
  [2, 'construct'],
  [2, 'combine'],
  [2, 'decon'],
  [3, 'flip'],
  [3, 'combine'],
  [4, 'flip'],
  [4, 'combine'],
];

let bashCmds = '';
combos.forEach(c => {
  cmd = `node simGenerator.js ${c[0]} ${c[1]} > exp${c[0]}_${c[1]}.py\n`
  bashCmds += cmd
})
console.log(bashCmds)


// let serverCmds = '';
// combos.forEach(c => {
//   screenCmd = `screen -S ${c[0]}-${c[1]}\n`
//   envCmd = `conda activate comlog\n`
//   pyCmd = `python exp${c[0]}_${c[1]}.py\n`
//   cmd = [ screenCmd, envCmd, pyCmd, '\n' ].join('')
//   serverCmds += cmd
// })
// console.log(serverCmds)
