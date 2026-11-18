const sidebar = document.querySelector('#sidebar');
const sidebarToggle = document.querySelector('#sidebarToggle');

if (sidebar && sidebarToggle) {
  const compacta = window.localStorage.getItem('vetcare-sidebar') === 'collapsed';

  const aplicarEstado = (collapsed) => {
    sidebar.classList.toggle('collapsed', collapsed);
    document.querySelector('.app-shell')?.classList.toggle('sidebar-collapsed', collapsed);
    sidebarToggle.setAttribute('aria-expanded', String(!collapsed));
    sidebarToggle.setAttribute('aria-label', collapsed ? 'Expandir menu lateral' : 'Recolher menu lateral');
    const logoutForm = sidebar.querySelector('.sidebar-logout-form');
    const logoutButton = sidebar.querySelector('.sidebar-logout');
    if (logoutForm) {
      logoutForm.style.width = collapsed && window.innerWidth > 760 ? '38px' : '96px';
      logoutForm.style.height = '34px';
      logoutForm.style.margin = '10px auto 0';
    }
    if (logoutButton) {
      logoutButton.style.width = collapsed && window.innerWidth > 760 ? '38px' : '96px';
      logoutButton.style.height = '34px';
      logoutButton.style.minHeight = '34px';
      logoutButton.style.maxHeight = '34px';
      logoutButton.style.lineHeight = '34px';
      logoutButton.style.margin = '0';
      logoutButton.style.padding = collapsed && window.innerWidth > 760 ? '0' : '0 12px';
    }
    sidebarToggle.title = collapsed ? 'Expandir menu' : 'Recolher menu';
  };

  aplicarEstado(compacta);
  window.addEventListener('resize', () => aplicarEstado(sidebar.classList.contains('collapsed')));

  sidebarToggle.addEventListener('click', () => {
    const collapsed = !sidebar.classList.contains('collapsed');
    aplicarEstado(collapsed);
    window.localStorage.setItem('vetcare-sidebar', collapsed ? 'collapsed' : 'expanded');
  });
}

document.querySelectorAll('.cpf-field').forEach(input => {
  input.addEventListener('input', () => {
    const digits = input.value.replace(/\D/g, '').slice(0, 11);
    input.value = digits.replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d{1,2})$/,'$1-$2');
  });
});

document.querySelectorAll('.edit-tutor').forEach(button => button.addEventListener('click', () => {
  const form = document.querySelector('#formEditarTutor');
  form.action = `/tutores/${button.dataset.id}/editar`;
  document.querySelector('#editNome').value = button.dataset.nome;
  document.querySelector('#editCpf').value = button.dataset.cpf;
  document.querySelector('#editTelefone').value = button.dataset.telefone;
  document.querySelector('#editEmail').value = button.dataset.email;
  document.querySelector('#editEndereco').value = button.dataset.endereco;
}));

document.querySelectorAll('.edit-pet').forEach(button => button.addEventListener('click', () => {
  const form = document.querySelector('#formEditarPet');
  form.action = `/pets/${button.dataset.id}/editar`;
  document.querySelector('#editPetNome').value = button.dataset.nome;
  document.querySelector('#editPetEspecie').value = button.dataset.especie;
  document.querySelector('#editPetRaca').value = button.dataset.raca;
  document.querySelector('#editPetSexo').value = button.dataset.sexo;
  document.querySelector('#editPetNascimento').value = button.dataset.nascimento;
  document.querySelector('#editPetObservacoes').value = button.dataset.observacoes;
  document.querySelector('#editPetTutor').value = button.dataset.tutor;
}));

document.addEventListener('pointerdown', (event) => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ripple = document.createElement('span');
  ripple.className = 'click-ripple';
  ripple.style.left = `${event.clientX}px`;
  ripple.style.top = `${event.clientY}px`;
  document.body.appendChild(ripple);
  ripple.addEventListener('animationend', () => ripple.remove());
});

const agoraLocal = new Date();
const deslocamento = agoraLocal.getTimezoneOffset() * 60000;
const minimoLocal = new Date(agoraLocal.getTime() - deslocamento).toISOString().slice(0,16);
document.querySelectorAll('input[type="datetime-local"]').forEach(input => {
  input.min = minimoLocal;
});

document.querySelectorAll('.edit-agendamento').forEach(button => button.addEventListener('click', () => {
  const form = document.querySelector('#formEditarAgendamento');
  form.action = `/agendamentos/${button.dataset.id}/editar`;
  document.querySelector('#editAgendamentoPet').value = button.dataset.pet;
  document.querySelector('#editAgendamentoData').value = button.dataset.data;
  document.querySelector('#editAgendamentoObs').value = button.dataset.observacao;
  document.querySelector('#editAgendamentoStatus').value = button.dataset.status;
}));
