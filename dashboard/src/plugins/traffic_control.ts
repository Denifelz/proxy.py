/*
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable, TLS interception capable
    proxy server for Application debugging, testing and development.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
*/
import { DashboardPlugin } from '../core/plugin'

export class TrafficControlPlugin extends DashboardPlugin {
  public name: string = 'traffic_control'

  public initializeTab () : JQuery<HTMLElement> {
    return this.makeTab('Traffic Controls', 'fa-lock')
  }

  public initializeSkeleton (): JQuery<HTMLElement> {
    return $('<div></div>')
  }

  public activated (): void {}

  public deactivated (): void {}
}
