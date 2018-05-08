one.addEventListener('mouseover', function(){
  two.classList.add('bright')
})
one.addEventListener('mouseout', function(){
  two.classList.remove('bright')
})
two.addEventListener('mouseover', function(){
  one.classList.add('bright')
})
two.addEventListener('mouseout', function(){
  one.classList.remove('bright')
})
