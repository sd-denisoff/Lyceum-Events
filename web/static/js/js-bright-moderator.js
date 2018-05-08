one.addEventListener('mouseover', function(){
  two.classList.add('bright')
  three.classList.add('bright')
})
one.addEventListener('mouseout', function(){
  two.classList.remove('bright')
  three.classList.remove('bright')
})
two.addEventListener('mouseover', function(){
  one.classList.add('bright')
  three.classList.add('bright')
})
two.addEventListener('mouseout', function(){
  one.classList.remove('bright')
  three.classList.remove('bright')
})
three.addEventListener('mouseover', function(){
  one.classList.add('bright')
  two.classList.add('bright')
})
three.addEventListener('mouseout', function(){
  one.classList.remove('bright')
  two.classList.remove('bright')
})
