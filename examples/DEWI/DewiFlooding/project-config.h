#ifndef __PROJECT_CONFIG_H__
#define __PROJECT_CONFIG_H__




#undef   NETSTACK_CONF_RDC
#define  NETSTACK_CONF_RDC     nullrdc_driver

#undef   NETSTACK_CONF_FRAMER
#define  NETSTACK_CONF_FRAMER  framer_802154

#undef   NETSTACK_CONF_MAC
#define  NETSTACK_CONF_MAC     csma_driver

#undef   NETSTACK_CONF_NETWORK
#define  NETSTACK_CONF_NETWORK rime_driver

//#undef FRAME802154_CONF_VERSION
//#define FRAME802154_CONF_VERSION FRAME802154_IEEE802154E_2012
#endif /* __PROJECT_CONFIG_H__ */