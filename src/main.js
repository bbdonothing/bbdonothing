const steps = document.querySelector('.card ul');
const footer = document.createElement('p');
footer.innerHTML =
  'After syncing with Capacitor, open the native projects and run on your emulator or device.';
steps.after(footer);

console.info('Web assets ready for Capacitor webview shells.');
