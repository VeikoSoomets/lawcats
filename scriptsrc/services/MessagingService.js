/**
 * Messaging service class.
 */

import toastr from 'toastr';

class MessagingService {
  
  constructor () {
    this.messageTime = 5000;
  }

  /**
   * Send an info message to the user.
   * @param {String} message The message to send.
   * @param {Number} time    Optional time of toast.
   */
  info (message, time) {
    let timeOut = time || this.messageTime;
    toastr.info(message, null, {timeOut});
  }

  /**
   * Send a success message to the user.
   * @param {String} message The message to send.
   * @param {Number} time    Optional time of toast.
   */
  success (message, time) {
    let timeOut = time || this.messageTime;
    toastr.success(message, null, {timeOut});
  }

  /**
   * Send an danger message to the user.
   * @param {String} message The message to send.
   * @param {Number} time    Optional time of toast.
   */
  danger (message, time) {
    let timeOut = time || this.messageTime;
    toastr.error(message, null, {timeOut});
  }
}

export default MessagingService;