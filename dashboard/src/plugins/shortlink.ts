/*
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable, TLS interception capable
    proxy server for Application debugging, testing and development.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
*/

import { DashboardPlugin} from "../core/plugin";

export class ShortlinkPlugin extends DashboardPlugin {
  constructor (name: string) {
    super(name);
  }

  public initializeTab() : JQuery<HTMLElement> {
    return $('<a/>')
      .attr({
        href: '#',
        id: 'proxyShortLinks'
      })
      .addClass('nav-link')
      .text('Short Links')
      .prepend(
        $('<i/>')
          .addClass('fa')
          .addClass('fa-fw')
          .addClass('fa-bolt')
      )
  }

  public initializeAppSkeleton(): JQuery<HTMLElement> {
    return $('<div></div>')
  }

  public activated(): void {
    throw new Error("Method not implemented.");
  }

  public deactivated(): void {
    throw new Error("Method not implemented.");
  }
}
