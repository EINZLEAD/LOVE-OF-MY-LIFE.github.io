// Simple gallery and letters stored in localStorage
(function(){
  const PHOTO_KEY = 'lovelife_photos_v1'
  const LETTER_KEY = 'lovelife_letters_v1'

  const photoInput = document.getElementById('photo-input')
  const galleryGrid = document.getElementById('gallery-grid')
  const clearPhotosBtn = document.getElementById('clear-photos')

  const letterForm = document.getElementById('letter-form')
  const lettersList = document.getElementById('letters-list')
  const clearLettersBtn = document.getElementById('clear-letters')

  const modal = document.getElementById('img-modal')
  const modalImg = document.getElementById('modal-img')
  const modalCaption = document.getElementById('modal-caption')
  const modalClose = document.getElementById('modal-close')
  const deletePhotoBtn = document.getElementById('delete-photo')

  let photos = JSON.parse(localStorage.getItem(PHOTO_KEY) || '[]')
  let letters = JSON.parse(localStorage.getItem(LETTER_KEY) || '[]')
  let currentIndex = null

  function savePhotos(){ localStorage.setItem(PHOTO_KEY, JSON.stringify(photos)) }
  function saveLetters(){ localStorage.setItem(LETTER_KEY, JSON.stringify(letters)) }

  function renderGallery(){
    galleryGrid.innerHTML = ''
    if(!photos.length){ galleryGrid.innerHTML = '<p class="muted">No photos yet — add one above.</p>'; return }
    photos.forEach((src, i)=>{
      const div = document.createElement('div'); div.className='item'
      const img = document.createElement('img'); img.src = src; img.alt = `Photo ${i+1}`
      img.addEventListener('click', ()=>openModal(i))
      div.appendChild(img)
      galleryGrid.appendChild(div)
    })
  }

  function renderLetters(){
    lettersList.innerHTML = ''
    if(!letters.length){ lettersList.innerHTML = '<p class="muted">No letters yet — write one above.</p>'; return }
    letters.slice().reverse().forEach((l, idx)=>{
      const card = document.createElement('article'); card.className='card'
      const h3 = document.createElement('h3'); h3.textContent = l.title
      const p = document.createElement('p'); p.textContent = l.body
      const meta = document.createElement('div'); meta.style.marginTop='8px'; meta.style.display='flex'; meta.style.justifyContent='space-between'
      const date = document.createElement('small'); date.className='muted'; date.textContent = new Date(l.created).toLocaleString()
      const del = document.createElement('button'); del.className='btn ghost'; del.textContent='Delete';
      del.addEventListener('click', ()=>{ if(confirm('Delete this letter?')){ letters.splice(letters.length-1-idx,1); saveLetters(); renderLetters() } })
      meta.appendChild(date); meta.appendChild(del)
      card.appendChild(h3); card.appendChild(p); card.appendChild(meta)
      lettersList.appendChild(card)
    })
  }

  function openModal(i){ currentIndex = i; modalImg.src = photos[i]; modalCaption.textContent = `${i+1} of ${photos.length}`; modal.setAttribute('aria-hidden','false') }
  function closeModal(){ modal.setAttribute('aria-hidden','true'); modalImg.src=''; currentIndex=null }

  photoInput.addEventListener('change', e=>{
    const file = e.target.files && e.target.files[0]
    if(!file) return
    const reader = new FileReader()
    reader.onload = ()=>{ photos.push(reader.result); savePhotos(); renderGallery(); photoInput.value = '' }
    reader.readAsDataURL(file)
  })

  clearPhotosBtn.addEventListener('click', ()=>{ if(confirm('Clear all saved photos?')){ photos=[]; savePhotos(); renderGallery() } })

  deletePhotoBtn.addEventListener('click', ()=>{
    if(currentIndex==null) return
    if(confirm('Delete this photo?')){ photos.splice(currentIndex,1); savePhotos(); renderGallery(); closeModal() }
  })

  modalClose.addEventListener('click', closeModal)
  modal.addEventListener('click', e=>{ if(e.target===modal) closeModal() })

  letterForm.addEventListener('submit', e=>{
    e.preventDefault()
    const title = document.getElementById('letter-title').value.trim()
    const body = document.getElementById('letter-body').value.trim()
    if(!title || !body) return
    letters.push({title, body, created: Date.now()})
    saveLetters(); renderLetters(); letterForm.reset()
  })

  clearLettersBtn.addEventListener('click', ()=>{ if(confirm('Clear all letters?')){ letters=[]; saveLetters(); renderLetters() } })

  // initial render
  renderGallery(); renderLetters()
})();
