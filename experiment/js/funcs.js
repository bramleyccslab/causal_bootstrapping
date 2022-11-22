
/** Ad hoc setups */
const defaultStone = { 'borderWidth': '8px', 'mar': 5, 'len': 60 };
const smallStone = { 'borderWidth': '3px', 'mar': 3, 'len': 20 };
const maxBlocks = 16

/** Basic helper functions */
const readStripes= (stone) => parseInt(stone.replace(/[()]/g, '').split(',')[0])
const readDots= (stone) => parseInt(stone.replace(/[()]/g, '').split(',')[1])
const readLength = (stone) => parseInt(stone.replace(/[()]/g, '').split(',')[2])

function createCustomElement (type = 'div', className, id) {
  let element = (["svg", "polygon"].indexOf(type) < 0)?
    document.createElement(type):
    document.createElementNS("http://www.w3.org/2000/svg", type);
  if (className.length > 0) element.setAttribute("class", className);
  element.setAttribute("id", id);
  return element;
}
function createDivWithStyle (className = "div", id = "", style = "") {
  let element = createCustomElement('div', className, id);
  setStyle(element, style);
  return element;
}
function createText(h = "h1", text = 'hello') {
  let element = document.createElement(h);
  let tx = document.createTextNode(text);
  element.append(tx);
  return(element)
}
function setAttributes(el, attrs) {
  for(var key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
}
function createBtn (btnId, text = "Button", on = true, className = "task-button") {
  let btn = createCustomElement("button", className, btnId);
  btn.disabled = !on;
  (text.length > 0) ? btn.append(document.createTextNode(text)): null;
  return(btn)
}

/** Task functions */
function createInitStones(config, parentDiv, learnDivPrefix) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-${config.trial}`)
  agentDiv.append(createAgentStone(`${learnDivPrefix}-${config.trial}-agent`, config.agentSvg))
  recipientDiv.append(createBlocks(`${learnDivPrefix}-${config.trial}-recipient`, config))
  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createInitHistory(config, parentDiv, learnDivPrefix, showText = true) {
  let spaceDiv = createCustomElement("div", "display-main-space", `${learnDivPrefix}-displaymainspace-hist-${config.trial}`)
  let agentDiv = createCustomElement("div", "display-main-agent", `${learnDivPrefix}-displaymainagent-hist-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${learnDivPrefix}-displaymainrecipient-hist-${config.trial}`)

  if (showText) {
    let textDiv = createCustomElement('div', 'hist-text', id=`learn${config.trial}-hist-text`)
    textDiv.append(createText('h2', 'Before'))
    spaceDiv.append(textDiv);
  }
  agentDiv.append(createAgentStone(`${learnDivPrefix}-${config.trial}-hist-agent`, config.agentSvg))
  recipientDiv.append(createBlocks(`${learnDivPrefix}-${config.trial}-hist-recipient`, config))

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function createSum(config, divPrefix) {
  let sumBox = createCustomElement('div', 'summary-box', `${divPrefix}-box-${config.trial}`);

  let sumBoforeDiv = createCustomElement("div", "display-hist", `${divPrefix}-beforediv-${config.trial}`);
  sumBoforeDiv = createSumBefore(config, sumBoforeDiv, divPrefix)

  let sumAfterDiv = createCustomElement("div", "display-after", `${divPrefix}-afterdiv-${config.trial}`);
  sumAfterDiv = createSumAfter(config, sumAfterDiv, divPrefix)

  sumBox.append(sumBoforeDiv)
  sumBox.append(sumAfterDiv)
  return sumBox
}
function createSumBefore(config, parentDiv, divPrefix) {
  let agentDiv = createCustomElement("div", "display-main-agent", `${divPrefix}-displaymainagent-after-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${divPrefix}-displaymainrecipient-after-${config.trial}`)

  agentDiv.append(createAgentStone(`${divPrefix}-${config.trial}-after-agent`, config.agentSvg))
  recipientDiv.append(createBlocks(`${divPrefix}-${config.trial}-after-recipient`, config))

  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);

}
function createSumAfter(config, parentDiv, divPrefix) {
  let agentDiv = createCustomElement("div", "display-main-agent-after", `${divPrefix}-displaymainagent-after-${config.trial}`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${divPrefix}-displaymainrecipient-after-${config.trial}`)

  agentDiv.append(createAgentStone(`${divPrefix}-${config.trial}-after-agent`, config.agentSvg))
  recipientDiv.append(createBlocks(`${divPrefix}-${config.trial}-after-recipient`, config, false))

  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)
  return(parentDiv);
}
function getAgentStoneSvg(agent = '(1,1,1)', color='red', base = 40, r = 25) {
  let nStripes = readStripes(agent)
  let nDots = readDots(agent)
  const getDelta = (x) => (-x + Math.sqrt(2*(r**2)-x**2))/2

  let circleSvg = `<circle class="agent-stone" cx="${base}" cy="${base}" r="${r+5}" />`

  switch (nStripes) {
    case 1:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />`;
      break;
    case 2:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(15)}" y1="${base-getDelta(15)-15}" x2="${base-getDelta(15)-15}" y2="${base+getDelta(15)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(15)+15}" y1="${base-getDelta(15)}" x2="${base-getDelta(15)}" y2="${base+getDelta(15)+15}" stroke="${color}" />`
      break;
    case 3:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(0)}" y1="${base-getDelta(0)}" x2="${base-getDelta(0)}" y2="${base+getDelta(0)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)}" y1="${base-getDelta(20)-20}" x2="${base-getDelta(20)-20}" y2="${base+getDelta(20)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(20)+20}" y1="${base-getDelta(20)}" x2="${base-getDelta(20)}" y2="${base+getDelta(20)+20}" stroke="${color}" />`
      break;
    case 4:
      stripes = `<line class="agent-stone-stripe" x1="${base+getDelta(8)}" y1="${base-getDelta(8)-8}" x2="${base-getDelta(8)-8}" y2="${base+getDelta(8)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(8)+8}" y1="${base-getDelta(8)}" x2="${base-getDelta(8)}" y2="${base+getDelta(8)+8}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)}" y1="${base-getDelta(25)-25}" x2="${base-getDelta(25)-25}" y2="${base+getDelta(25)}" stroke="${color}" />` + '\n' +
      `<line class="agent-stone-stripe" x1="${base+getDelta(25)+25}" y1="${base-getDelta(25)}" x2="${base-getDelta(25)}" y2="${base+getDelta(25)+25}" stroke="${color}" />`
      break;
    default:
      stripes = ''
  }

  return (circleSvg + stripes + '\n' + addDots(nDots))

}
function createAgentStone(id, svgText='') {
  let agentDiv = createCustomElement("div", "agent-stone-div", `${id}-div`);
  let agentStoneSvg = createCustomElement('svg', 'stone-svg', id)
  agentStoneSvg.innerHTML = svgText
  agentDiv.append(agentStoneSvg)
  return agentDiv
}
function createBlocks(id, stoneOpts, isInit = true, after = false) {
  let div = createCustomElement("div", "recipient-stone-div", `${id}-blocks-all`);
  let length = isInit? readLength(stoneOpts.recipient) : readLength(stoneOpts.result)
  let max =  (stoneOpts.phase=='gen')? maxBlocks: Math.max(readLength(stoneOpts.result), readLength(stoneOpts.recipient))
  for(let i = 0; i < max; i++ ) {
    let block = createCustomElement("div", "recipient-block", `${id}-block-${i}`)
    block.style.opacity = (i < length)? 1 : (stoneOpts.phase=='gen' && after)? blockOpDecay(i, length) : 0
    div.append(block)
  }
  return(div);
}
function createGenStones(config, parentDiv, genDivPrefix, after = false) {
  let phase = (after==0)? 'before': 'after';
  let agentCSS =  (after==0)? 'display-main-agent': 'display-main-agent-after';

  let spaceDiv = createCustomElement("div", "display-main-space", `${genDivPrefix}-${config.trial}-display-space-${phase}-div`)
  let agentDiv = createCustomElement("div", agentCSS, `${genDivPrefix}-${config.trial}-display-agent-${phase}-div`)
  let recipientDiv = createCustomElement("div", "display-main-recipient", `${genDivPrefix}-${config.trial}-display-recipient-${phase}-div`)

  agentDiv.append(createAgentStone(`${genDivPrefix}-${config.trial}-agent-${phase}`, config.agentSvg));
  recipientDiv.append(createBlocks(`${genDivPrefix}-${config.trial}-recipient-${phase}`, config, true, after));

  parentDiv.append(spaceDiv)
  parentDiv.append(agentDiv)
  parentDiv.append(recipientDiv)

  return(parentDiv);
}
function blockOpDecay(index, base) {
  if ((index === base) && (index < maxBlocks)) {
    return 0.15
  } else {
    if ((index === base+1) && (index < maxBlocks)) {
      return 0.05
    } else {
      return 0
    }
  }
  // return (index > base + 1)? 0: 0.1 - 0.001*(index - base)
}
function genBlocksEffects(config, genDivPrefix, genClicked) {
  // if (genClicked[config.trial-1] == 0) {

  // }
  let box = document.getElementById(`${genDivPrefix}-displaymain-${config.trial}`)
  box.onclick = (event) => {
    let blockLeft = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-blocks-all`).getBoundingClientRect().left;
    if (event.clientX < blockLeft) {
      hideBlocks(config, genDivPrefix)
      genClicked[config.trial-1] += 1
      document.getElementById(`${genDivPrefix}-confirm-btn-${config.trial}`).disabled = false
      document.getElementById(`${genDivPrefix}-reset-btn-${config.trial}`).disabled = false
    }
  }
  for(let i = 0; i < maxBlocks; i++ ) {
    let idPrefix = `${genDivPrefix}-${config.trial}-recipient-after-block-`
    let base = readLength(config.recipient)
    let blockDiv = document.getElementById(`${idPrefix}${i}`)
    blockDiv.onmousemove = () => highlightBlocksOnMouseOver(idPrefix, i, base)
    blockDiv.onmouseout = () => highlightBlocksOnly(idPrefix, i, base)
    blockDiv.onclick = () => {
      highlightBlocks(idPrefix, i, base)
      if (genClicked[config.trial-1] % 2 == 1) {
        for(let i = 0; i < maxBlocks; i++ ) {
          let blockDiv = document.getElementById(`${idPrefix}${i}`)
          blockDiv.onmousemove = () => highlightBlocksOnMouseOver(idPrefix, i, base)
          blockDiv.onmouseout = () => highlightBlocksOnly(idPrefix, i, base)
        }
      } else {
        for(let i = 0; i < maxBlocks; i++ ) {
          let blockDiv = document.getElementById(`${idPrefix}${i}`)
          blockDiv.onmousemove = () => null
          blockDiv.onmouseout = () => null
        }
      }
      genClicked[config.trial-1] += 1
    }
  }
}
function handleGenSelection(config,genDivPrefix) {
  let blocksDiv = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-blocks-all`)
  let resetBtn = document.getElementById(`${genDivPrefix}-reset-btn-${config.trial}`)
  let confirmBtn = document.getElementById(`${genDivPrefix}-confirm-btn-${config.trial}`)
  blocksDiv.onclick = () => {
    resetBtn.disabled = false
    confirmBtn.disabled = false
  }
}
function getCurrentSelection(config, genDivPrefix) {
  let blockOps = []
  for(let i = 0; i < maxBlocks; i++ ) {
    blockOps.push(document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-block-${i}`).style.opacity)
  }
  return(findAllIndex('1',blockOps).length)
}
function disableBlocks(config, genDivPrefix) {
  document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-blocks-all`).onclick = null
  for(let i = 0; i < maxBlocks; i++ ) {
    let blockDiv = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-block-${i}`)
    blockDiv.onmousemove = () => null
    blockDiv.onmouseout = () => null
    blockDiv.onclick = () => null
  }
}
function highlightBlocksOnMouseOver(idPrefix, i, base) {
  let baseBlocks = Array.from(Array(base).keys()).map(m => `${idPrefix}${m}`)
  let yesBlocks = Array.from(Array(maxBlocks).keys()).filter(b => (b <= i)).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i+2).map(m => `${idPrefix}${m}`)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=0)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=0.5)
  if (i+1 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+1}`).style.opacity = 0.15
  }
  if (i+2 < maxBlocks) {
    document.getElementById(`${idPrefix}${i+2}`).style.opacity = 0.05
  }
  if (i>=base) {
    baseBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  }
}
function highlightBlocks(idPrefix, i, base) {
  // let baseBlocks = Array.from(Array(base).keys()).map(m => `${idPrefix}${m}`)
  let yesBlocks = Array.from(Array(maxBlocks).keys()).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  yesBlocks.forEach(b => document.getElementById(b).style.opacity=1)
  noBlocks.forEach(b => document.getElementById(b).style.opacity=0)
  // if (i+1 < maxBlocks) {
  //   document.getElementById(`${idPrefix}${i+1}`).style.opacity = 0.15
  // }
  // if (i+2 < maxBlocks) {
  //   document.getElementById(`${idPrefix}${i+2}`).style.opacity = 0.05
  // }
  // baseBlocks.forEach(b => document.getElementById(b).style.opacity=1)
}
function highlightBlocksOnly(idPrefix, i) {
  let yesBlocks = Array.from(Array(maxBlocks).keys()).map(m => `${idPrefix}${m}`)
  let noBlocks = Array.from(Array(maxBlocks).keys()).filter(b => b > i).map(m => `${idPrefix}${m}`)
  if (i==0) {
    yesBlocks.forEach(b => document.getElementById(b).style.opacity=0)
    noBlocks.forEach(b => document.getElementById(b).style.opacity=0)
  } else {
    yesBlocks.forEach(b => document.getElementById(b).style.opacity=1)
    noBlocks.forEach(b => document.getElementById(b).style.opacity=0)
  }
}
function hideBlocks(config, genDivPrefix) {
  for(let i = 0; i < maxBlocks; i++ ) {
    let block = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-block-${i}`)
    block.style.opacity = 0
    block.onmousemove = () => {}
    block.onmouseout = () => {}
  }

}
function resetGenBlock(config, genDivPrefix, genClicked) {
  let length = readLength(config.recipient)
  for(let i = 0; i < maxBlocks; i++ ) {
    let block = document.getElementById(`${genDivPrefix}-${config.trial}-recipient-after-block-${i}`)
    block.style.opacity = (i < length)? 1 : blockOpDecay(i, length)
  }
  genBlocksEffects(config, genDivPrefix, genClicked)
}
function createPolygon(className, id, sides, scale) {
  let polygon = createCustomElement("polygon", className, id);

  n = parseInt(sides);
  let output = [];
  let adjust = (n===5)? 55 : 0;

  let mar = (scale==='default')? defaultStone.mar: smallStone.mar;
  let len = (scale==='default')? defaultStone.len: smallStone.len;

  if (n === 3) {
    output.push(`${len/2},${mar}`);
    output.push(`${len-mar},${len-mar}`);
    output.push(`${mar},${len-mar}`);
  } else if (n === 4) {
    output.push(`${mar},${mar}`);
    output.push(`${len-mar},${mar}`);
    output.push(`${len-mar},${len-mar}`);
    output.push(`${mar},${len-mar}`);
  } else {
    // Adapted from https://gist.github.com/jonthesquirrel/e2807811d58a6627ded4
    for (let i = 1; i <= n; i++) {
      output.push(
        ((len/2 * Math.cos(adjust + 2 * i * Math.PI / n)) + len/2).toFixed(0).toString() + "," +
        ((len/2 * Math.sin(adjust + 2 * i * Math.PI / n)) + len/2).toFixed(0).toString()
      )
    }
  }
  setAttributes(polygon, { "points": output.join(" ") });
  return(polygon);
}
function getDotPos(base=40, maxR=30) {
  let angle =  Math.floor(Math.random() * 90)
  let direction = Math.floor(Math.random() * 4)
  let sr = Math.floor(Math.random() * maxR)
  let sx = sr * Math.sin(angle)
  let sy = sr * Math.cos(angle)
  switch (direction) {
    case 0:
      x = base + sx
      y = base - sy
      break;
    case 1:
      x = base + sy
      y = base + sx
      break;
    case 2:
      x = base - sx
      y = base + sy
      break;
    case 3:
      x = base - sy
      y = base - sx
      break;
  }
  return({'x': x, 'y': y})
}
function isOverlapWith(pos1, pos2, delta = 20) {
  let distance = Math.sqrt((pos1.x-pos2.x)**2 + (pos1.y-pos2.y)**2)
  return (distance < delta)
}
function getDots (n, base=40, maxR=28) {
  let dotPos = []
  if (n<2) {
    dotPos.push(getDotPos(base, maxR))
  } else {
    while(dotPos.length < n) {
      let newPos = getDotPos(base, maxR)
      let overlap = 0
      for (let i=0; i<dotPos.length; i++) {
        let isOverlap = isOverlapWith(newPos, dotPos[i])
        overlap += isOverlap
      }
      if (overlap==0) {
        dotPos.push(newPos)
      }
    }
  }
  return dotPos
}
function addDots(n, base=40, maxR=26, color="black", size=4) {
  if (n==0) {
    return ''
  } else {
    const dotPos = getDots(n, base, maxR)
    let dotHTML = []
    for (let i=0; i<dotPos.length; i++) {
      dotHTML.push(`<circle cx="${dotPos[i].x}" cy="${dotPos[i].y}" r="${size}" stroke="${color}" stroke-width="${size}"/>`)
    }
    return dotHTML.join('\n')
  }
}
function clearElement (id) {
  let clear = document.getElementById(id);
  clear.remove();
}
function clearInitStones(learnDivPrefix, config) {
  clearElement(`${learnDivPrefix}-displaymainspace-${config.trial}`)
  clearElement(`${learnDivPrefix}-displaymainagent-${config.trial}`)
  clearElement(`${learnDivPrefix}-displaymainrecipient-${config.trial}`)
}
function getCurrentLocation (id) {
  let rect = {top: 0, bottom: 0, left: 0, right: 0};
  const pos = document.getElementById(id).getBoundingClientRect();
  rect.top = pos.top;
  rect.bottom = pos.bottom;
  rect.left = pos.left;
  rect.right = pos.right;
  return rect;
}

function playEffects (config, learnDivPrefix, clicked=0, demo=false) {

  if (!(document.body.contains(document.getElementById(`${learnDivPrefix}-${config.trial}-agent-div`)))) {
    console.log('???')
  }

  const agentStone = document.getElementById(`${learnDivPrefix}-${config.trial}-agent-div`);
  const startPos = getCurrentLocation(`${learnDivPrefix}-${config.trial}-agent`).right;
  const endPos = getCurrentLocation(`${learnDivPrefix}-${config.trial}-recipient-blocks-all`).left;

  const delta = Math.round(endPos - startPos) + 8;
  (delta > 0) && (agentStone.style.left = `${delta}px`);

  let initLen = readLength(config.recipient)
  let targetLen = readLength(config.result)

   if (demo==false) {
    let hist = document.getElementById(`${learnDivPrefix}-displayhist-${config.trial}`)
    if (targetLen == initLen) {
      setTimeout(()=> {
        hist.style.opacity = 0
        hist.style.display = 'flex'
        fadeIn(hist)
      }, 2500)
    } else if (targetLen < initLen) {
      setTimeout(() => {
        for (let i = initLen; i > targetLen; i-- ) {
          fadeOut(document.getElementById(`${learnDivPrefix}-${config.trial}-recipient-block-${i-1}`))
          if (clicked == 0) {
            setTimeout(()=> {
              hist.style.opacity = 0
              hist.style.display = 'flex'
              fadeIn(hist)
            }, 1000)
          }
        }
      }, 1500);
    } else {
      setTimeout(() => {
        for (let i = initLen; i < targetLen; i++ ) {
          fadeIn(document.getElementById(`${learnDivPrefix}-${config.trial}-recipient-block-${i}`))
          if (clicked == 0) {
            setTimeout(()=> {
              hist.style.opacity = 0
              hist.style.display = 'flex'
              fadeIn(hist)
            }, 1000)
          }
        }
      }, 1500);
    }
  } else {
    showQuestionMark(document.getElementById(`${learnDivPrefix}-${config.trial}-recipient-block-${initLen}`))
  }
}
function showQuestionMark (blockDiv) {
  blockDiv.innerHTML = '<p style="font-size:30px;color:red ">??<p>'
  blockDiv.style.backgroundColor = "white"
  blockDiv.style.borderWidth = 0
  blockDiv.style.opacity = 1
}
function fadeIn(element) {
  let op = 0.1;
  let timer = setInterval(() => {
    if (op >= 1) {
        clearInterval(timer);
    }
    element.style.opacity = op;
    element.style.filter = 'alpha(opacity=' + op * 100 + ")";
    op += op * 0.1;
  }, 20);
}
function fadeOut(element) {
  let op = 1;
  let timer = setInterval(() => {
    if (op <= 0) {
        clearInterval(timer);
    }
    element.style.opacity = op;
    element.style.filter = 'alpha(opacity=' + op * 100 + ")";
    op -= op * 0.1;
  }, 20);
}
function showNext(id, display = "flex", center = true) {
  let div = document.getElementById(id);
  div.style.display = display;
  div.scrollIntoView(center);
}
function hide(id) {
  let div = document.getElementById(id);
  div.style.display = "none";
}
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array
}
function disableFormInputs (formId) {
  const form = document.getElementById(formId);
  const inputs = form.elements;
  (Object.keys(inputs)).forEach((input) => inputs[input].disabled = true);
}
function isFilled (formID) {
  let notFilled = false;
  const nulls = [ '', '--', '', '--', '', '--' ];
  const form = document.getElementById(formID);
  const inputs = form.elements;
  (Object.keys(inputs)).forEach((input, idx) => {
    let field = inputs[input];
    notFilled = (notFilled || (field.value === nulls[idx]));
  });
  return (!notFilled)
}
function findAllIndex(element, array) {
  let indices = [];
  let idx = array.indexOf(element);
  while (idx != -1) {
    indices.push(idx);
    idx = array.indexOf(element, idx + 1);
  }
  return(indices);
}
function compIsFilled () {
  let radios = document.getElementsByTagName('input');
  let checked = 0;
  for (let i = 0; i < radios.length; i++) {
      checked += radios[i].checked;
  }
  return (checked > checks.length-1)
}
function removeSpecial (text) {
  text = text.replace(/[&\/\\#,$~%"\[\]{}@^_|`']/gi, '');
  text = text.replace(/(\r\n|\n|\r|\t)/gm, " ")
  return text
}
function showPostCheckPage (isPass) {
  const pageDiv = isPass? 'pass' : 'retry';
  document.getElementById('check-btn').style.display = 'none';
  document.getElementById(pageDiv).style.display = 'flex';
}
function showCompletion(code, nCorrect) {
  hide("debrief")
  showNext("completed")
  let bonusVal = nCorrect * 0.02
  bonusVal = Math.round(bonusVal*100)/100
  let t = document.createTextNode(code);
  let co = createText('p', `You got ${nCorrect} predictions correct!
  You will get £${bonusVal} bonus on top of your base pay.
  Bonus for writing the correct causal relationships will be paid after manual checks.`)
  // let returnLink = createCustomElement('p', '', '')
  // returnLink.innerHTML = `Click <a href='https://app.prolific.co/submissions/complete?cc=${code}'>here</a> to redirect to Prolific.`
  document.getElementById('completion-code').append(t);
  document.getElementById('completed').append(co);
  // document.getElementById('completed').append(returnLink);
}
function generateToken (length) {
  let tokens = '';
  let chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  for (let i = 0; i < length; i ++) {
      tokens += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return tokens;
}
function formatDates (date, option = 'date') {
  let year = date.getFullYear();
  let month = String(date.getMonth() + 1).padStart(2, '0');
  let day = String(date.getDate() + 1).padStart(2, '0');
  let hour = String(date.getHours()+ 1).padStart(2, '0');
  let min = String(date.getMinutes() + 1).padStart(2, '0');
  let sec = String(date.getSeconds() + 1).padStart(2, '0');
  dateParts = (option === 'date') ? [ year, month, day ] : [ hour, min, sec ];
  return dateParts.join('_');
}
function download(content, fileName, contentType) {
  var a = document.createElement("a");
  var file = new Blob([content], {type: contentType});
  a.href = URL.createObjectURL(file);
  a.download = fileName;
  a.click();
}
/** Data functions */
// // Experiment 2
// function prepConfigs(type) {
//   let setups = {
//     'learnA': [],
//     'genA': [],
//     'learnB': [],
//     'genB': [],
//     'genC': [],
//   }
//   if (type=='comp_mult') {
//     setups.learnA = [7, 10, 13]
//     setups.genA = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.learnB = [67, 50, 33]
//     setups.genB = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.genC = [100, 55, 94, 71, 31, 19, 41, 3]
//   } else if (type=='comp_mult_reverse') {
//     setups.learnA = [67, 50, 33]
//     setups.genA = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.learnB = [7, 10, 13]
//     setups.genB = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.genC = [100, 55, 94, 71, 31, 19, 41, 3]
//   } else if (type=='comp_const') {
//     setups.learnA = [7, 10, 13]
//     setups.genA = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.learnB = [27, 47, 67]
//     setups.genB = [100, 55, 94, 71, 31, 19, 41, 3]
//     setups.genC = [100, 55, 94, 71, 31, 19, 41, 3]
//   } else {
//     console.log('Cond type not found')
//   }
//   return setups
// }
// // Experiment 3
// function prepConfigs(type) {
//   let setups = {}
//   if (type==='sub') {
//     setups = {
//       'learnA': [27, 31, 35],
//       'genA': [100, 71, 78, 55, 47, 83, 9, 3],
//       'learnB': [23, 42, 61],
//       'genB': [100, 71, 78, 55, 47, 83, 9, 3],
//       'genC': [100, 71, 78, 55, 47, 83, 9, 3],
//     }
//   } else {
//     setups = {
//       'learnA': [23, 42, 61],
//       'genA': [100, 71, 78, 55, 47, 83, 9, 3],
//       'learnB': [27, 31, 35],
//       'genB': [100, 71, 78, 55, 47, 83, 9, 3],
//       'genC': [100, 71, 78, 55, 47, 83, 9, 3],
//     }
//   }
//   return setups
// }
// // Experiment 4
// function prepConfigs(type) {
//   let setups = {}
//   if (type==='sub') {
//     setups = {
//       'learnA': [7, 10, 13],
//       'genA': [100, 55, 94, 71, 31, 19, 41, 3],
//       'learnB': [27, 47, 67],
//       'genB': [100, 55, 94, 71, 31, 19, 41, 3],
//       'genC': [100, 55, 94, 71, 31, 19, 41, 3],
//     }
//   } else {
//     setups = {
//       'learnA': [27, 47, 67],
//       'genA': [100, 55, 94, 71, 31, 19, 41, 3],
//       'learnB': [7, 10, 13],
//       'genB': [100, 55, 94, 71, 31, 19, 41, 3],
//       'genC': [100, 55, 94, 71, 31, 19, 41, 3],
//     }
//   }
//   return setups
// }
// // Experiment 1
// function prepConfigs(type) {
//   let setups = {
//     'learnA': [],
//     'genA': [],
//     'learnB': [],
//     'genB': [],
//     'genC': [],
//   }
//   // if (type=='simple_easy') {
//   //   setups.learnA = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==2 && readLength(c.recipient)<4).map(c => c.trial_id)
//   //   setups.genA = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==2 && readLength(c.recipient)==4).map(c => c.trial_id)
//   //   setups.learnB = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)<4 && readLength(c.recipient)==2).map(c => c.trial_id)
//   //   setups.genB = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==4 && readLength(c.recipient)==2).map(c => c.trial_id)
//   //   setups.genC = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)!=2 && readLength(c.recipient)!=2).map(c => c.trial_id)
//   // } else if (type=='simple_hard') {
//   //   setups.learnA = config.filter(c => readDots(c.agent)<1 && readLength(c.result)==4).map(c => c.trial_id)
//   //   setups.genA = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==3 && readLength(c.recipient)==2).map(c => c.trial_id)
//   //   setups.learnB = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==1 && readLength(c.recipient)<4).map(c => c.trial_id)
//   //   setups.genB = config.filter(c => readDots(c.agent)<1 && readStripes(c.agent)==1 && readLength(c.recipient)==4).map(c => c.trial_id)
//   //   setups.genC = config.filter(c => readDots(c.agent)<1 && [setups.learnA, setups.learnB, setups.genA, setups.genB].flat().indexOf(c.trial_id) < 0).map(c => c.trial_id)
//   // } else
//   if (type=='comp_mult') {
//     setups.learnA = [23, 42, 61]
//     setups.genA = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.learnB = [35, 50, 65]
//     setups.genB = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.genC = [100, 71, 78, 55, 47, 83, 9, 3]
//   } else if (type=='comp_mult_reverse') {
//     setups.learnA = [35, 50, 65]
//     setups.genA = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.learnB = [23, 42, 61]
//     setups.genB = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.genC = [100, 71, 78, 55, 47, 83, 9, 3]
//   } else if (type=='comp_const') {
//     setups.learnA = [23, 42, 61]
//     setups.genA = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.learnB = [27, 31, 35]
//     setups.genB = [100, 71, 78, 55, 47, 83, 9, 3]
//     setups.genC = [100, 71, 78, 55, 47, 83, 9, 3]
//   } else if (type=='comp_subs') {
//     setups.learnA = config.filter(c => readDots(c.agent)<4 && readStripes(c.agent)==1 && readLength(c.recipient)==3).map(c => c.trial_id)
//     setups.genA = config.filter(c => readDots(c.agent)==1 && readStripes(c.agent)==3 && readLength(c.recipient)==4).map(c => c.trial_id)
//     setups.learnB = [12,24,36]
//     setups.genB = [21]
//     setups.genC = config.filter(c => [setups.learnA, setups.learnB, setups.genA, setups.genB].flat().indexOf(c.trial_id) < 0).map(c => c.trial_id)
//   } else if (type=='comp_subs_reverse') {
//     setups.learnA = [12,24,36]
//     setups.genA = [21]
//     setups.learnB = config.filter(c => readDots(c.agent)<4 && readStripes(c.agent)==1 && readLength(c.recipient)==3).map(c => c.trial_id)
//     setups.genB = config.filter(c => readDots(c.agent)==1 && readStripes(c.agent)==3 && readLength(c.recipient)==4).map(c => c.trial_id)
//     setups.genC = config.filter(c => [setups.learnA, setups.learnB, setups.genA, setups.genB].flat().indexOf(c.trial_id) < 0).map(c => c.trial_id)
//   } else if (type=='comp_comp') {
//     setups.learnA = [3,16,33]
//     setups.genA = [17]
//     setups.learnB = config.filter(c => readDots(c.agent)<4 && readStripes(c.agent)==1 && readLength(c.recipient)==3).map(c => c.trial_id)
//     setups.genB = config.filter(c => readDots(c.agent)==1 && readStripes(c.agent)==3 && readLength(c.recipient)==4).map(c => c.trial_id)
//     setups.genC = config.filter(c => [setups.learnA, setups.learnB, setups.genA, setups.genB].flat().indexOf(c.trial_id) < 0).map(c => c.trial_id)
//   } else {
//     console.log('Cond type not found')
//   }
//   return setups
// }
// Demo
function prepConfigs() {
  let setups = {
      'learnA': [23, 42, 61],
      'genA': [100, 71, 78, 55, 47, 83, 9, 3],
      'learnB': [35, 50, 65],
      'genB': [100, 71, 78, 55, 47, 83, 9, 3],
      'genC': [100, 71, 78, 55, 47, 83, 9, 3],
  }
  return setups
}

function fmtConfig(dataArr, batch, phase, agentColor = 'tomato') {
  let fmtted = []
  dataArr.forEach((data, idx) => {
    dd = {}
    dd['id'] =`t${data['trial_id']}`
    dd['trial'] = idx+1
    dd['batch'] = batch
    dd['phase'] = phase
    dd['agent'] = data['agent'].replace(/\s/g, '');
    dd['recipient'] = data['recipient'].replace(/\s/g, '');
    dd['result'] = data['result'].replace(/\s/g, '');
    dd['alter'] = dd['result'];//data['alter'].replace(/\s/g, '');
    dd['color'] = agentColor
    dd['agentSvg'] = getAgentStoneSvg(dd['agent'], agentColor)
    fmtted.push(dd)
  })
  return fmtted
}
function prepTrialData (configsArr) {
  let trialData = {
    "batch": [],
    "phase": [],
    "trial": [],
    "id": [],
    "agent": [],
    "agent-color": [],
    "recipient": [],
    "result": [],
    "alter": [],
    "selection": [],
    "correct": [],
    "gtCorrect": [],
  }
  configsArr.forEach(conf => {
    trialData['batch'].push(conf['batch']);
    trialData['phase'].push(conf['phase']);
    trialData['trial'].push(conf['trial']);
    trialData['id'].push(conf['id']);
    trialData['agent'].push(conf['agent']);
    trialData['agent-color'].push(conf['color']);
    trialData['recipient'].push(conf['recipient']);
    trialData['result'].push(conf['result']);
    trialData['alter'].push(conf['alter']);
    trialData['selection'].push('--');
    trialData['correct'].push(0);
    trialData['gtCorrect'].push(0);
  })
  return trialData
}

/** Page functions */
function createLearnTask(learnDivPrefix, learnConfig, total=0, isMainTask = true) {
  let trialId = learnConfig.trial;
  let display = (mode==='dev'|trialId===1)? 'flex': 'none';

  let box = createCustomElement("div", "box", `${learnDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "task-box", `${learnDivPrefix}-taskbox-${trialId}`);

  if (total > 1) {
    let taskNum = createText('h2', trialId); //`${trialId}/${total}`
    taskBox.append(taskNum);
  }

  let displayBox = createCustomElement("div", "display-box", `${learnDivPrefix}-displaybox-${trialId}`);
  let displayMain = createCustomElement("div", "display-main", `${learnDivPrefix}-displaymain-${trialId}`);
  displayMain = createInitStones(learnConfig, displayMain, learnDivPrefix);

  let displayHist = createCustomElement("div", "display-hist", `${learnDivPrefix}-displayhist-${trialId}`);
  displayHist = createInitHistory(learnConfig, displayHist, learnDivPrefix)
  displayHist.style.opacity = 0
  isMainTask? displayBox.append(displayHist): null;
  displayBox.append(displayMain)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${learnDivPrefix}-test-btn-${trialId}`, "Test", true));
  isMainTask? buttonGroup.append(createBtn(`${learnDivPrefix}-next-btn-${trialId}`, "Next", false)) : null;
  taskBox.append(displayBox);

  // taskBox.append(buttonGroup);
  box.append(taskBox);
  box.append(buttonGroup)
  box.style.display = display;

  return box
}
function createInputForm(formPrefix, isSecond=false) {
  let box = createCustomElement("div", "box", `${formPrefix}-box`);
  let emphaseText = isSecond? 'Please account for <b>all</b> the magic eggs you have checked, and ': 'Please ';
  box.innerHTML = `
          <div class="display-box" id="${formPrefix}-display-box">
            <form class="input-form" id="${formPrefix}-input-form">
              <p>
                <b>What is your best guess about these magic eggs?</b>
                (${emphaseText}be specific about <i>what properties you think matter or do not matter for the effects,
                and how they do so</i>.)
                <br />
              </p>
              <textarea name="${formPrefix}_input" id="${formPrefix}_input" placeholder="Type here"></textarea>
              <!-- <p class="incentive">Remember there is a bonus if you guess correctly, and nonsense answers will result in a zero bonus or hit rejection.</p> -->
              <p>How certain are you?
                <select name="${formPrefix}_certainty" id="${formPrefix}_certainty" class="input-rule">
                  <option value="--" SELECTED>
                    <option value="10">10 - Very certain</option>
                    <option value="9">9</option>
                    <option value="8">8</option>
                    <option value="7">7</option>
                    <option value="6">6</option>
                    <option value="5">5 - Moderately</option>
                    <option value="4">4</option>
                    <option value="3">3</option>
                    <option value="2">2</option>
                    <option value="1">1</option>
                    <option value="0">0 - Not sure at all</option>
                </select>
              </p>
            </form>
          </div>
          <div class="button-group-vc" id="${formPrefix}-button-group-vc">
            <button id="${formPrefix}-input-submit-btn" disabled=true>OK</button>
          </div>`
  return box
}
function createMindChangeForm(formPrefix) {
  let div = createCustomElement("div", "box", `${formPrefix}-wrapper`);
  let boolBox = createCustomElement("div", "display-box-min", `${formPrefix}-bool-box`);
  boolBox.innerHTML = `
    <form class="input-form" id="${formPrefix}-bool-form">
      <p>Did you change your mind?
        <input type="radio" name="alice-change" value=1>Yes
        <input type="radio" name="alice-change" value=0>No
      </p>
    </form>`
  let box = createCustomElement("div", "display-box", `${formPrefix}-box`);
  box.innerHTML = `
            <form class="input-form" id="${formPrefix}-input-form">
              <p>
                <b>What is your guess about these magic eggs now?</b>
                (Please be specific about <i>what properties you think matter or do not matter for the effects,
                and how they do so</i>.)
                <br />
              </p>
              <textarea name="${formPrefix}_input" id="${formPrefix}_input" placeholder="Type here"></textarea>
              <!-- <p class="incentive">Remember there is a bonus if you guess correctly, and nonsense answers will result in a zero bonus or hit rejection.</p> -->
              <p>How certain are you?
                <select name="${formPrefix}_certainty" id="${formPrefix}_certainty" class="input-rule">
                  <option value="--" SELECTED>
                    <option value="10">10 - Very certain</option>
                    <option value="9">9</option>
                    <option value="8">8</option>
                    <option value="7">7</option>
                    <option value="6">6</option>
                    <option value="5">5 - Moderately</option>
                    <option value="4">4</option>
                    <option value="3">3</option>
                    <option value="2">2</option>
                    <option value="1">1</option>
                    <option value="0">0 - Not sure at all</option>
                </select>
              </p>
            </form>
            </div>
          `
  box.style.display = 'none'

  let btns = createCustomElement("div", "button-group-vc", `${formPrefix}-button-group-vc`);
  btns.innerHTML = `<button id="${formPrefix}-input-submit-btn" disabled=true>OK</button>`
  div.append(boolBox)
  div.append(box)
  div.append(btns)
  return div
}
function createGenTask(genDivPrefix, genConfigs, total=0) {
  let trialId = genConfigs.trial

  let box = createCustomElement("div", "box", `${genDivPrefix}-box-${trialId}`);
  let taskBox = createCustomElement("div", "gen-task-box", `${genDivPrefix}-taskbox-${trialId}`);

  // if (total > 1) {
  //   let taskNum = createText('h2', `${trialId}/${total}`);
  //   taskBox.append(taskNum);
  // }

  let taskNumText = (total>1)? `[${trialId}/${total}] `: '';

  let beforeMain = createCustomElement("div", "display-main", `${genDivPrefix}-beforemain-${trialId}`);
  beforeMain = createGenStones(genConfigs, beforeMain, genDivPrefix);

  let displayBox = createCustomElement("div", "display-box-2", `${genDivPrefix}-displaybox-${trialId}`);
  let displayMain = createCustomElement("div", "display-main", `${genDivPrefix}-displaymain-${trialId}`);
  displayMain = createGenStones(genConfigs, displayMain, genDivPrefix, true);

  displayBox.append(createText('h2', taskNumText + 'What will the blocks look like if touched by the magic egg?'))
  displayBox.append(beforeMain)
  displayBox.append(createText('h3', 'Make your prediction by clicking on the blocks:'))
  displayBox.append(displayMain)

  const buttonGroup = createCustomElement("div", "button-group-vc", `learn${trialId}`);
  buttonGroup.append(createBtn(`${genDivPrefix}-reset-btn-${trialId}`, "Reset", false));
  buttonGroup.append(createBtn(`${genDivPrefix}-confirm-btn-${trialId}`, "Confirm", false));

  taskBox.append(displayBox);
  // taskBox.append(buttonGroup);
  box.append(taskBox);
  box.append(buttonGroup);

  return box
}
